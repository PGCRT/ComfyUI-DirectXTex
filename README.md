# CRT-DirectXTex

DDS Load/Save nodes for ComfyUI.

## Prerequisites (Windows)

- Visual Studio 2022 Build Tools
- MSVC v143 C++ toolset
- Windows 10/11 SDK
- CMake 3.15+

Everything else is handled by `build.bat` (DirectXTex download + Python deps + build).

## Install

1. Put this folder in `ComfyUI/custom_nodes/CRT-DirectXTex`
2. Open a terminal in this folder
3. Run:

```bat
build.bat
```

4. Wait for success message (`dds_pybind.pyd` copied in folder root)
5. Restart ComfyUI

## Included nodes

- Load DDS (CRT)
- Save DDS (CRT)

## Workflow example

Example workflow is in the `workflows/` folder.
