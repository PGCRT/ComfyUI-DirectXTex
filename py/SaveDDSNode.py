import os
import torch
import numpy as np
import folder_paths

try:
    import dds_pybind

    HAS_DDS_BINDING = True
except ImportError:
    HAS_DDS_BINDING = False


class SaveDDSNode:
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        output_dir = folder_paths.get_output_directory()
        return {
            "required": {
                "image": ("IMAGE",),
                "folder_path": (
                    "STRING",
                    {
                        "default": output_dir,
                        "tooltip": "Base folder path. Defaults to ComfyUI's output folder.",
                    },
                ),
                "filename": (
                    "STRING",
                    {
                        "default": "output",
                        "tooltip": "Base file name without extension.",
                    },
                ),
                "format": (
                    "STRING",
                    {
                        "default": "DXGI_FORMAT_BC3_UNORM",
                        "tooltip": "DDS format (e.g., DXGI_FORMAT_BC1_UNORM, DXGI_FORMAT_BC3_UNORM).",
                    },
                ),
                "alpha": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "Include alpha channel in output DDS.",
                    },
                ),
                "force_bc7": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "Force BC7 compression instead of BC3.",
                    },
                ),
            },
            "optional": {
                "mask": ("MASK", {"tooltip": "Optional mask to use as alpha channel."}),
                "format_override": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Format from LoadDDSNode to preserve original format.",
                    },
                ),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_dds"
    CATEGORY = "CRT/Save"
    DESCRIPTION = "Saves images as DDS texture files."

    def save_dds(
        self,
        image,
        folder_path,
        filename,
        format,
        alpha,
        force_bc7,
        mask=None,
        format_override="",
    ):
        if image is None:
            return ()

        if not HAS_DDS_BINDING:
            print("❌ dds_pybind module not available. Please build the extension.")
            return ()

        try:
            filename_clean = filename.strip().lstrip("/\\")

            if not filename_clean:
                raise ValueError("Filename field cannot be empty.")

            final_dir = folder_path.strip()
            os.makedirs(final_dir, exist_ok=True)

            if force_bc7:
                use_format = "DXGI_FORMAT_BC7_UNORM"
            else:
                use_format = (
                    format_override.strip()
                    if format_override.strip()
                    else format.strip()
                )
            if not use_format:
                use_format = "DXGI_FORMAT_BC3_UNORM"

            print(
                f"   Using format: {use_format}, alpha={alpha}, force_bc7={force_bc7}"
            )

            batch_size = image.shape[0]
            has_mask = mask is not None
            print(
                f"   DEBUG saver: has_mask={has_mask}, mask_type={type(mask)}, mask_shape={mask.shape if mask is not None else None}"
            )
            mask_batch = None
            if has_mask:
                if mask.ndim == 3 and mask.shape[0] == 1 and batch_size == 1:
                    mask_batch = 1
                elif mask.ndim == 2:
                    mask = mask.unsqueeze(0)
                    mask_batch = 1
                elif mask.ndim == 3:
                    mask_batch = mask.shape[0]
                print(
                    f"   DEBUG saver: mask_batch={mask_batch}, mask_shape={mask.shape}, mask_min={mask.min().item():.3f}, mask_max={mask.max().item():.3f}"
                )

            for i in range(batch_size):
                if batch_size > 1:
                    base_filename = f"{filename_clean}_{i + 1}"
                else:
                    base_filename = filename_clean

                filepath_to_check = os.path.join(final_dir, f"{base_filename}.dds")
                final_filepath = filepath_to_check
                counter = 1
                while os.path.exists(final_filepath):
                    final_filepath = os.path.join(
                        final_dir, f"{base_filename}_{counter}.dds"
                    )
                    counter += 1

                img_tensor = image[i]
                if img_tensor.device.type != "cpu":
                    img_tensor = img_tensor.cpu()
                img_np = img_tensor.numpy()
                img_np = (img_np * 255).astype(np.uint8)

                if img_np.ndim == 2:
                    img_np = np.stack([img_np] * 3, axis=-1)
                elif img_np.shape[2] == 4:
                    img_np = img_np[:, :, :3]

                if not alpha:
                    use_format_save = (
                        "DXGI_FORMAT_BC1_UNORM"
                        if "BC3" in use_format or "BC7" in use_format
                        else use_format
                    )
                    output_data = img_np
                    print(f"   Saving as RGB, format: {use_format_save}")
                else:
                    use_format_save = use_format
                    alpha_channel = np.full(
                        (img_np.shape[0], img_np.shape[1]), 255, dtype=np.uint8
                    )
                    if has_mask:
                        if mask_batch == 1:
                            mask_np = mask.cpu().numpy()
                            if mask_np.ndim == 3 and mask_np.shape[0] == 1:
                                mask_np = mask_np.squeeze(0)
                        else:
                            mask_np = mask[i].cpu().numpy()
                        if mask_np.ndim == 3 and mask_np.shape[2] == 1:
                            mask_np = mask_np.squeeze(2)
                        mask_np = np.clip(mask_np, 0, 1)
                        alpha_channel = (mask_np * 255).astype(np.uint8)
                        print(
                            f"   Using mask: min={alpha_channel.min()}, max={alpha_channel.max()}"
                        )
                    output_data = np.zeros(
                        (img_np.shape[0], img_np.shape[1], 4), dtype=np.uint8
                    )
                    output_data[:, :, :3] = img_np
                    output_data[:, :, 3] = alpha_channel

                dds_data = dds_pybind.save_dds_to_memory(
                    output_data, use_format_save, False
                )

                with open(final_filepath, "wb") as f:
                    f.write(dds_data)

                print(f"✅ Saved DDS to: {final_filepath} Format: {use_format}")

            return ()

        except Exception as e:
            print(f"❌ ERROR in SaveDDSNode: {str(e)}")
            raise e


NODE_CLASS_MAPPINGS = {"SaveDDSNode": SaveDDSNode}
NODE_DISPLAY_NAME_MAPPINGS = {"SaveDDSNode": "Save DDS (CRT)"}
