import os
import sys
import sysconfig
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import subprocess

DIRECTX_TEX_DIR = Path(__file__).parent / "DirectXTex-main" / "DirectXTex-main"

SOURCES = [
    "dds_pybind.cpp",
]

DIRECTX_TEX_SOURCES = [
    str(DIRECTX_TEX_DIR / "DirectXTex" / "BC.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "BC4BC5.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "BC6HBC7.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexCompress.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexConvert.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexDDS.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexHDR.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexImage.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexMipmaps.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexMisc.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexNormalMaps.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexPMAlpha.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexResize.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexTGA.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexUtil.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexFlipRotate.cpp"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexWIC.cpp"),
]

DIRECTX_TEX_HEADERS = [
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTex.h"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTex.inl"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DirectXTexP.h"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "BC.h"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "DDS.h"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "filters.h"),
    str(DIRECTX_TEX_DIR / "DirectXTex" / "scoped.h"),
    str(DIRECTX_TEX_DIR / "Common" / "d3dx12.h"),
]

INCLUDE_PATHS = [
    str(DIRECTX_TEX_DIR),
    str(DIRECTX_TEX_DIR / "DirectXTex"),
    str(DIRECTX_TEX_DIR / "Common"),
]

EXTRA_COMPILE_ARGS = [
    "/std:c++17",
    "/EHsc",
    "/W3",
    "/D_WIN32_WINNT=0x0A00",
    "/DNOMINMAX",
    "/DUNICODE",
    "/D_UNICODE",
]

EXTRA_LINK_ARGS = [
    "/DYNAMICBASE",
    "/NXCOMPAT",
]

if sys.platform == "win32":
    EXTRA_COMPILE_ARGS.extend(
        [
            "/permissive-",
            "/Zc:__cplusplus",
            "/utf-8",
        ]
    )


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = str(Path(sourcedir).resolve())


class CMakeBuild(build_ext):
    def build_extension(self, ext):
        ext_fullpath = Path(self.build_lib) / Path(self.get_ext_fullpath(ext.name))
        build_temp = Path(self.build_temp) / ext.name
        install_dir = self.build_lib

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY:{install_dir}",
            f"-DPYTHON_EXECUTABLE:{sys.executable}",
            f"-DCMAKE_BUILD_TYPE=Release",
            f"-DBUILD_SHARED_LIBS=ON",
            f"-DBUILD_DX11=OFF",
            f"-DBUILD_DX12=OFF",
            f"-DBUILD_TOOLS=OFF",
            f"-DBUILD_SAMPLE=OFF",
            f"-DENABLE_OPENEXR_SUPPORT=OFF",
            f"-DENABLE_LIBJPEG_SUPPORT=OFF",
            f"-DENABLE_LIBPNG_SUPPORT=OFF",
            f"-DBC_USE_OPENMP=OFF",
        ]

        build_args = ["--config", "Release"]

        try:
            import numpy as np

            INCLUDE_PATHS.append(np.get_include())
        except ImportError:
            pass

        os.makedirs(build_temp, exist_ok=True)

        for path in INCLUDE_PATHS:
            cmake_args.append(f"-DCMAKE_INCLUDE_PATH:{path}")

        if not os.path.exists(build_temp / "CMakeCache.txt"):
            cmake = "cmake"
            result = subprocess.run(
                [cmake, ext.sourcedir] + cmake_args,
                cwd=build_temp,
                capture_output=True,
            )
            if result.returncode != 0:
                print("CMake stdout:", result.stdout.decode("utf-8", errors="replace"))
                print("CMake stderr:", result.stderr.decode("utf-8", errors="replace"))
                raise RuntimeError("CMake configuration failed")

        result = subprocess.run(
            ["cmake", "--build", ".", "--parallel"] + build_args,
            cwd=build_temp,
            capture_output=True,
        )
        if result.returncode != 0:
            print("Build stdout:", result.stdout.decode("utf-8", errors="replace"))
            print("Build stderr:", result.stderr.decode("utf-8", errors="replace"))
            raise RuntimeError("CMake build failed")


ext_modules = [CMakeExtension("dds_pybind", sourcedir=".")]

setup(
    name="dds_pybind",
    version="1.0.0",
    author="CRT",
    description="Python bindings for DirectXTex DDS operations",
    ext_modules=ext_modules,
    cmdclass={"build_ext": CMakeBuild},
    zip_safe=False,
)
