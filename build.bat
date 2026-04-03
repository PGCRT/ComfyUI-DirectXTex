@echo off
setlocal

cd /d "%~dp0"

echo ================================================
echo Building dds_pybind extension for ComfyUI
echo ================================================
echo.

set "COMFY_PY=%~dp0..\..\..\python_embeded\python.exe"
if exist "%COMFY_PY%" (
  echo Using ComfyUI Python: "%COMFY_PY%"
) else (
  echo [WARN] ComfyUI python not found at "%COMFY_PY%"
  echo [WARN] Falling back to system python on PATH.
  set "COMFY_PY=python"
)

if not exist "DirectXTex-main\DirectXTex-main\DirectXTex\BC.cpp" (
  echo.
  echo DirectXTex source not found. Downloading...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $zip='DirectXTex-main.zip'; $url='https://github.com/microsoft/DirectXTex/archive/refs/heads/main.zip'; if (Test-Path 'DirectXTex-main') { Remove-Item -Recurse -Force 'DirectXTex-main' }; if (Test-Path $zip) { Remove-Item -Force $zip }; Invoke-WebRequest -Uri $url -OutFile $zip; New-Item -ItemType Directory -Path 'DirectXTex-main' -Force | Out-Null; Expand-Archive -Path $zip -DestinationPath 'DirectXTex-main' -Force; Remove-Item -Force $zip"
  if errorlevel 1 goto :fail_download
)

if not exist "DirectXTex-main\DirectXTex-main\DirectXTex\BC.cpp" goto :fail_layout

echo.
echo Installing Python build dependencies...
"%COMFY_PY%" -m pip install -r requirements.txt
if errorlevel 1 goto :fail_pip

if exist build (
  echo Cleaning old build directory...
  rmdir /s /q build 2>nul
)

mkdir build
cd build

echo.
echo Configuring with CMake...
cmake .. -G "Visual Studio 17 2022" -A x64 -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON -DBUILD_DX11=OFF -DBUILD_DX12=OFF -DBUILD_TOOLS=OFF -DBUILD_SAMPLE=OFF -DENABLE_OPENEXR_SUPPORT=OFF -DENABLE_LIBJPEG_SUPPORT=OFF -DENABLE_LIBPNG_SUPPORT=OFF -DBC_USE_OPENMP=OFF -DPYTHON_EXECUTABLE="%COMFY_PY%"
if errorlevel 1 goto :fail_cmake

echo.
echo Building dds_pybind...
cmake --build . --config Release --parallel
if errorlevel 1 goto :fail_build

echo.
if exist "Release\dds_pybind.pyd" (
  copy /y "Release\dds_pybind.pyd" "..\dds_pybind.pyd" >nul
  echo Copied dds_pybind.pyd to project root.
) else (
  echo [WARN] Release\dds_pybind.pyd not found. Copy manually from build output.
)

echo.
echo ================================================
echo Build successful.
echo Restart ComfyUI.
echo ================================================
echo.
pause
exit /b 0

:fail_download
echo.
echo [ERROR] Failed to download/extract DirectXTex.
goto :end_fail

:fail_layout
echo.
echo [ERROR] DirectXTex layout invalid.
echo Expected: DirectXTex-main\DirectXTex-main\DirectXTex\BC.cpp
goto :end_fail

:fail_pip
echo.
echo [ERROR] Failed to install Python requirements.
goto :end_fail

:fail_cmake
echo.
echo [ERROR] CMake configuration failed.
goto :end_fail

:fail_build
echo.
echo [ERROR] Build failed.

:end_fail
echo.
echo Press any key to close.
pause >nul
exit /b 1
