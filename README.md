# CRT-DirectXTex (Build-It-Yourself)

This custom node uses a native Python extension (`dds_pybind.pyd`) for DDS loading/saving.

This repository is source-first. End users are expected to build the extension locally.

## What this node provides

- `Load DDS (CRT)`
- `Save DDS (CRT)`

Python node scripts are in `py/`.

## Prerequisites (Windows)

You need all of the following:

1. **Windows 10/11 x64**
2. **Visual Studio 2022 Build Tools** with:
   - MSVC v143 C++ toolset
   - Windows 10/11 SDK
3. **CMake** (3.15+)
4. **Use ComfyUI's Python for build and runtime**
   - You can have any Python version installed on your system.
   - But the `.pyd` must be built with the same Python interpreter ComfyUI uses.
   - In portable installs, that is usually `python_embeded/python.exe`.
5. Python packages (installed into ComfyUI Python):
   - `setuptools`, `wheel`, `pybind11`, `numpy`

Why this matters:

- A `.pyd` is ABI-specific. If you build it with one Python and Comfy loads it with another, import fails.

## Required source layout

`setup.py` and `CMakeLists.txt` use DirectXTex sources at:

`DirectXTex-main/DirectXTex-main/`

`build.bat` now auto-downloads and extracts DirectXTex if that layout is missing.

Expected files after auto-download:

- `DirectXTex-main/DirectXTex-main/DirectXTex/BC.cpp`
- `DirectXTex-main/DirectXTex-main/DirectXTex/DirectXTex.h`

## Build steps

Run from this folder (`custom_nodes/CRT-DirectXTex`):

### Option A: Build with batch script

```bat
build.bat
```

What `build.bat` does:

1. Uses ComfyUI Python if found (`..\..\..\python_embeded\python.exe`)
2. Auto-downloads DirectXTex sources if missing
3. Installs `requirements.txt`
4. Configures/builds with CMake
5. Copies `dds_pybind.pyd` to this folder root

### Option B: Build with Python setuptools

Use ComfyUI's Python executable (example path below, adjust to your install):

```bat
"<COMFY_ROOT>\python_embeded\python.exe" -m pip install -U pip
"<COMFY_ROOT>\python_embeded\python.exe" -m pip install -r requirements.txt
"<COMFY_ROOT>\python_embeded\python.exe" setup.py build_ext --inplace
```

After build, ensure this file exists:

- `dds_pybind.pyd`

## Install in ComfyUI

1. Put this folder under `ComfyUI/custom_nodes/CRT-DirectXTex`
2. Ensure `dds_pybind.pyd` is in the folder root
3. Restart ComfyUI

## Verify

In ComfyUI, search for:

- `Load DDS (CRT)`
- `Save DDS (CRT)`

If they do not appear, check startup logs for `dds_pybind` import errors.

## Common issues

### `ImportError: DLL load failed` or `Module not found`

- Python ABI mismatch (built with different Python version)
- Missing MSVC runtime
- Wrong architecture (non-x64)

### CMake cannot find compiler

- Install Visual Studio Build Tools and reopen terminal
- Confirm `cl.exe` is available in environment

### Missing DirectXTex source files

- Ensure `DirectXTex-main/DirectXTex-main` exists with DirectXTex sources

## Node Manager / dependencies

- If ComfyUI-Manager installs this node and `requirements.txt` is present, it will install Python dependencies automatically.
- System toolchain requirements (Visual Studio C++ Build Tools, Windows SDK, CMake) are **not** handled by pip.

## Notes

- `build/` and `__pycache__/` are build artifacts and can be removed from release source.
- Keep `dds_pybind.cpp`, `CMakeLists.txt`, and `setup.py` for user-side builds.
