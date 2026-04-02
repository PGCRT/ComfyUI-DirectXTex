import os
from pathlib import Path
import torch
import numpy as np

try:
    import dds_pybind

    HAS_DDS_BINDING = True
except ImportError:
    HAS_DDS_BINDING = False


class LoadDDSNode:
    def __init__(self):
        self.cache = {}

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder_path": ("STRING", {"default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "crawl_subfolders": ("BOOLEAN", {"default": False}),
                "suffix_whitelist": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Comma-separated suffixes to filter files. Only files containing these suffixes will be loaded. Example: _d,_n",
                    },
                ),
                "suffix_blacklist": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Comma-separated suffixes to exclude files. Files containing these suffixes will be skipped. Example: _n,_m",
                    },
                ),
                "folder_blacklist": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Comma-separated folder names to exclude. Files inside these folders will be skipped. Example: sky,effects,cubemaps",
                    },
                ),
                "folder_suffix_blacklist": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Comma-separated folder suffixes to exclude. Folders ending with these suffixes will be skipped. Example: _lod,_temp,_old",
                    },
                ),
                "min_megapixels": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": 0.0,
                        "max": 100.0,
                        "step": 0.1,
                        "tooltip": "Minimum megapixel threshold. Images smaller than this (width * height / 1,000,000) will be skipped. 0 = no minimum.",
                    },
                ),
                "max_megapixels": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": 0.0,
                        "max": 100.0,
                        "step": 0.1,
                        "tooltip": "Maximum megapixel threshold. Images larger than this (width * height / 1,000,000) will be skipped. 0 = no maximum.",
                    },
                ),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("image_output", "mask", "folder_path", "filename", "format")
    FUNCTION = "load_dds_incrementally"
    CATEGORY = "CRT/Load"
    DESCRIPTION = "Loads DDS texture files incrementally based on seed."

    def load_dds_incrementally(
        self,
        folder_path,
        seed,
        crawl_subfolders,
        suffix_whitelist,
        suffix_blacklist,
        folder_blacklist,
        folder_suffix_blacklist,
        min_megapixels,
        max_megapixels,
    ):
        def create_blank_image():
            blank = np.zeros((512, 512, 4), dtype=np.float32)
            return torch.from_numpy(blank)[None,]

        def create_blank_mask():
            blank = np.zeros((512, 512), dtype=np.float32)
            return torch.from_numpy(blank)[None,]

        if not HAS_DDS_BINDING:
            print("❌ dds_pybind module not available. Please build the extension.")
            return (
                create_blank_image(),
                create_blank_mask(),
                "Error: dds_pybind not loaded",
                "",
                "DXGI_FORMAT_UNKNOWN",
            )

        if not folder_path or not folder_path.strip():
            return (
                create_blank_image(),
                create_blank_mask(),
                "Error: Folder path is empty",
                "",
                "DXGI_FORMAT_UNKNOWN",
            )

        folder = Path(folder_path.strip())
        if not folder.is_dir():
            print(f"❌ Error: Folder '{folder}' not found.")
            return (
                create_blank_image(),
                create_blank_mask(),
                "Error: Folder not found",
                "",
                "DXGI_FORMAT_UNKNOWN",
            )

        cache_key = (
            str(folder.resolve())
            + ("_sub" if crawl_subfolders else "")
            + f"_{suffix_whitelist}"
            + f"_{suffix_blacklist}"
            + f"_{folder_blacklist}"
            + f"_{folder_suffix_blacklist}"
            + f"_{min_megapixels}"
            + f"_{max_megapixels}"
        )
        current_mtime = folder.stat().st_mtime

        if (
            cache_key not in self.cache
            or self.cache[cache_key]["mtime"] != current_mtime
        ):
            print(f"🔎 Folder changed or not cached. Scanning '{folder}'...")
            try:
                path_iterator = (
                    folder.rglob("*") if crawl_subfolders else folder.glob("*")
                )
                files = [
                    p
                    for p in path_iterator
                    if p.is_file() and p.suffix.lower() == ".dds"
                ]

                # Step 1: Suffix whitelist (fast filename check)
                if suffix_whitelist.strip():
                    suffixes = [
                        s.strip() for s in suffix_whitelist.split(",") if s.strip()
                    ]
                    if suffixes:
                        files = [
                            f
                            for f in files
                            if any(s.lower() in f.name.lower() for s in suffixes)
                        ]

                # Step 2: Dimension check (expensive - opens files)
                # Do this after whitelist to minimize file reads
                # Dimension results are cached, so changing suffix_blacklist or folder_blacklist later
                # won't require re-scanning dimensions
                if min_megapixels > 0 or max_megapixels > 0:
                    filtered_files = []
                    skipped_small = 0
                    skipped_large = 0
                    for f in files:
                        try:
                            with open(f, "rb") as dds_file:
                                data = dds_file.read()
                            dds_format = dds_pybind.get_dds_format_from_memory(data)
                            image_data, fmt, width, height = (
                                dds_pybind.load_dds_from_memory(data)
                            )
                            megapixels = (width * height) / 1000000
                            keep_file = True
                            if min_megapixels > 0 and megapixels < min_megapixels:
                                keep_file = False
                                skipped_small += 1
                            if max_megapixels > 0 and megapixels > max_megapixels:
                                keep_file = False
                                skipped_large += 1
                            if keep_file:
                                filtered_files.append(f)
                        except Exception as e:
                            print(f"   Warning: Could not check size of {f.name}: {e}")
                            filtered_files.append(f)
                    files = filtered_files
                    if skipped_small > 0:
                        print(
                            f"   Skipped {skipped_small} files below {min_megapixels} MP threshold"
                        )
                    if skipped_large > 0:
                        print(
                            f"   Skipped {skipped_large} files above {max_megapixels} MP threshold"
                        )

                # Step 3: Suffix blacklist (fast - no file access needed)
                if suffix_blacklist.strip():
                    blacklist = [
                        s.strip() for s in suffix_blacklist.split(",") if s.strip()
                    ]
                    if blacklist:
                        files = [
                            f
                            for f in files
                            if not any(s.lower() in f.name.lower() for s in blacklist)
                        ]

                # Step 4: Folder blacklist (fast - no file access needed)
                if folder_blacklist.strip():
                    folder_exclusions = [
                        s.strip().lower()
                        for s in folder_blacklist.split(",")
                        if s.strip()
                    ]
                    if folder_exclusions:
                        files = [
                            f
                            for f in files
                            if not any(
                                excluded in p.lower()
                                for p in f.relative_to(folder).parts
                                for excluded in folder_exclusions
                            )
                        ]

                # Step 5: Folder suffix blacklist (fast - no file access needed)
                if folder_suffix_blacklist.strip():
                    folder_suffix_exclusions = [
                        s.strip().lower()
                        for s in folder_suffix_blacklist.split(",")
                        if s.strip()
                    ]
                    if folder_suffix_exclusions:
                        files = [
                            f
                            for f in files
                            if not any(
                                p.lower().endswith(suffix)
                                for p in f.relative_to(folder).parts
                                for suffix in folder_suffix_exclusions
                            )
                        ]

                files = sorted(files)
                self.cache[cache_key] = {"files": files, "mtime": current_mtime}
                filter_info = ""
                if suffix_whitelist.strip():
                    filter_info += f" (whitelist: {suffix_whitelist})"
                if suffix_blacklist.strip():
                    filter_info += f" (blacklist: {suffix_blacklist})"
                if folder_blacklist.strip():
                    filter_info += f" (folders: {folder_blacklist})"
                if folder_suffix_blacklist.strip():
                    filter_info += f" (folder suffixes: {folder_suffix_blacklist})"
                if min_megapixels > 0:
                    filter_info += f" (min: {min_megapixels} MP)"
                if max_megapixels > 0:
                    filter_info += f" (max: {max_megapixels} MP)"
                print(f"✅ Cached {len(files)} DDS files from '{folder}'{filter_info}")
            except Exception as e:
                print(f"❌ Error accessing folder '{folder}': {str(e)}")
                if cache_key in self.cache:
                    del self.cache[cache_key]
                return (
                    create_blank_image(),
                    create_blank_mask(),
                    "Error accessing folder",
                    "",
                    "DXGI_FORMAT_UNKNOWN",
                )

        files = self.cache[cache_key]["files"]

        if not files:
            print(f"❌ Warning: No DDS files found in '{folder}'.")
            return (
                create_blank_image(),
                create_blank_mask(),
                "No DDS files found",
                "",
                "DXGI_FORMAT_UNKNOWN",
            )

        num_files = len(files)
        selected_index = seed % num_files
        selected_file = files[selected_index]

        try:
            with open(selected_file, "rb") as f:
                data = f.read()

            dds_format = dds_pybind.get_dds_format_from_memory(data)
            image, format_str, width, height = dds_pybind.load_dds_from_memory(data)

            print(
                f"   DEBUG: image_array shape={image.shape}, min={image.min():.3f}, max={image.max():.3f}"
            )

            image_array = np.array(image, dtype=np.float32) / 255.0

            print(
                f"   DEBUG: image_array shape={image_array.shape}, min={image_array.min():.3f}, max={image_array.max():.3f}"
            )

            has_alpha = image_array.shape[2] == 4

            if has_alpha:
                mask_array = image_array[:, :, 3]
                print(
                    f"   DEBUG: alpha min={mask_array.min():.3f}, max={mask_array.max():.3f}"
                )
            else:
                mask_array = np.ones((height, width), dtype=np.float32)

            img_tensor = torch.from_numpy(image_array[:, :, :3])[None,]
            mask_tensor = torch.from_numpy(mask_array)[None,]

            print(
                f"✅ Seed {seed} → DDS {selected_index + 1}/{num_files}: '{selected_file.stem}' Format: {format_str}"
            )

            return (
                img_tensor,
                mask_tensor,
                str(selected_file.parent),
                selected_file.stem,
                dds_format,
            )

        except FileNotFoundError:
            print(
                f"❌ Error: File '{selected_file}' was in cache but not found on disk."
            )
            if cache_key in self.cache:
                del self.cache[cache_key]
            return (
                create_blank_image(),
                create_blank_mask(),
                "Error: Cached file not found",
                "",
                "DXGI_FORMAT_UNKNOWN",
            )
        except Exception as e:
            print(f"❌ Error loading DDS '{selected_file}': {str(e)}")
            return (
                create_blank_image(),
                create_blank_mask(),
                "Error loading DDS",
                "",
                "DXGI_FORMAT_UNKNOWN",
            )


NODE_CLASS_MAPPINGS = {"LoadDDSNode": LoadDDSNode}
NODE_DISPLAY_NAME_MAPPINGS = {"LoadDDSNode": "Load DDS (CRT)"}
