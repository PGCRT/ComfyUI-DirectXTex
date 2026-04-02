@echo off
setlocal enabledelayedexpansion

echo ================================================
echo Building dds_pybind extension for ComfyUI
echo ================================================
echo.

cd /d "%~dp0"

set "COMFY_PY=%~dp0..\..\..\python_embeded\python.exe"
if exist "%COMFY_PY%" (
    echo Using ComfyUI Python: "%COMFY_PY%"
) else (
    echo WARNING: ComfyUI python not found at "%COMFY_PY%"
    echo Falling back to system python on PATH.
    set "COMFY_PY=python"
)

if not exist "DirectXTex-main\DirectXTex-main\DirectXTex\BC.cpp" (
    echo.
    echo DirectXTex source not found. Downloading...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "^\
      $ErrorActionPreference='Stop'; ^\
      $zip='DirectXTex-main.zip'; ^\
      $url='https://github.com/microsoft/DirectXTex/archive/refs/heads/main.zip'; ^\
      if (Test-Path 'DirectXTex-main') { Remove-Item -Recurse -Force 'DirectXTex-main' }; ^\
      if (Test-Path $zip) { Remove-Item -Force $zip }; ^\
      Invoke-WebRequest -Uri $url -OutFile $zip; ^\
      New-Item -ItemType Directory -Path 'DirectXTex-main' -Force | Out-Null; ^\
      Expand-Archive -Path $zip -DestinationPath 'DirectXTex-main' -Force; ^\
      Remove-Item -Force $zip;"

    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo Failed to download/extract DirectXTex.
        pause
        exit /b 1
    )

    if not exist "DirectXTex-main\DirectXTex-main\DirectXTex\BC.cpp" (
        echo.
        echo DirectXTex layout still invalid after download.
        echo Expected: DirectXTex-main\DirectXTex-main\DirectXTex\BC.cpp
        pause
        exit /b 1
    )
)

echo.
echo Installing Python build dependencies...
"%COMFY_PY%" -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Failed to install Python requirements.
    pause
    exit /b 1
)

if exist build (
    echo Cleaning old build directory...
    rmdir /s /q build 2>nul
)

echo Creating build directory...
mkdir build
cd build

echo.
echo Configuring with CMake...
cmake .. -G "Visual Studio 17 2022" -A x64 ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DBUILD_SHARED_LIBS=ON ^
    -DBUILD_DX11=OFF ^
    -DBUILD_DX12=OFF ^
    -DBUILD_TOOLS=OFF ^
    -DBUILD_SAMPLE=OFF ^
    -DENABLE_OPENEXR_SUPPORT=OFF ^
    -DENABLE_LIBJPEG_SUPPORT=OFF ^
    -DENABLE_LIBPNG_SUPPORT=OFF ^
    -DBC_USE_OPENMP=OFF ^
    -DPYTHON_EXECUTABLE="%COMFY_PY%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo CMake configuration failed!
    echo.
    pause
    exit /b 1
)

echo.
echo Building dds_pybind...
cmake --build . --config Release --parallel

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Build successful!
echo ================================================
echo.
echo The dds_pybind.pyd file is ready.
echo.

if exist Release\dds_pybind.pyd (
    copy /y Release\dds_pybind.pyd ..\dds_pybind.pyd
    if %ERRORLEVEL% EQU 0 (
        echo Copied dds_pybind.pyd to: %~dp0
    )
) else (
    echo NOTE: dds_pybind.pyd not found in expected location.
    echo Please copy it manually to the CRT-DirectXTex directory.
)

echo.
echo To use the DDS nodes in ComfyUI:
echo 1. Make sure dds_pybind.pyd is in this directory
echo 2. Restart ComfyUI if it's running
echo.
pause
