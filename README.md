# ComfyUI-DirectXTex

DDS Load/Save nodes for ComfyUI.

## Prerequisites (Windows)

- Visual Studio 2022 Build Tools
- MSVC v143 C++ toolset
- Windows 10/11 SDK
- CMake 3.15+

Everything else is handled by `build.bat` (DirectXTex download + Python deps + build).

## Install

1. Clone into `ComfyUI/custom_nodes`:

```bat
git clone https://github.com/PGCRT/ComfyUI-DirectXTex ComfyUI-DirectXTex
```

2. Run `build.bat` (double-click it)
3. Wait for success message (`dds_pybind.pyd` copied in folder root)
4. Restart ComfyUI

## Included nodes

- Load DDS (CRT)
- Save DDS (CRT)

## Workflow example

Example workflow is in the `workflows/` folder.
