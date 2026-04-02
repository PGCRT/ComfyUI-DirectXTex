cmake_minimum_required(VERSION 3.15)
project(dds_pybind)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
set(BUILD_SHARED_LIBS ON)

set(Python3_EXECUTABLE "D:/DRIVE/ComfyUI_windows_portable/python_embeded/python.exe")
set(PYTHON_EXECUTABLE "D:/DRIVE/ComfyUI_windows_portable/python_embeded/python.exe")
set(Python3_ROOT_DIR "D:/DRIVE/ComfyUI_windows_portable/python_embeded")

find_package(Python3 COMPONENTS Interpreter Development)

set(pybind11_DIR "D:/DRIVE/ComfyUI_windows_portable/python_embeded/Lib/site-packages/pybind11/share/cmake/pybind11")
set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 REQUIRED)

if(CMAKE_VS_PLATFORM_NAME STREQUAL "ARM64EC")
    set(DIRECTX_ARCH "arm64ec")
endif()

if(CMAKE_VS_PLATFORM_NAME STREQUAL "ARM64")
    set(DIRECTX_ARCH "arm64")
endif()

set(DIRECTX_TEX_DIR "${CMAKE_CURRENT_SOURCE_DIR}/DirectXTex-main/DirectXTex-main")

set(DIRECTX_TEX_SOURCES
    ${DIRECTX_TEX_DIR}/DirectXTex/BC.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/BC4BC5.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/BC6HBC7.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexCompress.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexConvert.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexDDS.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexHDR.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexImage.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexMipmaps.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexMisc.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexNormalMaps.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexPMAlpha.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexResize.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexTGA.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexUtil.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexFlipRotate.cpp
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexWIC.cpp
)

set(DIRECTX_TEX_HEADERS
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTex.h
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTex.inl
    ${DIRECTX_TEX_DIR}/DirectXTex/DirectXTexP.h
    ${DIRECTX_TEX_DIR}/DirectXTex/BC.h
    ${DIRECTX_TEX_DIR}/DirectXTex/DDS.h
    ${DIRECTX_TEX_DIR}/DirectXTex/filters.h
    ${DIRECTX_TEX_DIR}/DirectXTex/scoped.h
    ${DIRECTX_TEX_DIR}/Common/d3dx12.h
)

include_directories(
    ${DIRECTX_TEX_DIR}
    ${DIRECTX_TEX_DIR}/DirectXTex
    ${DIRECTX_TEX_DIR}/Common
    ${Python3_INCLUDE_DIRS}
)

add_compile_options(
    /EHsc
    /W3
    /D_WIN32_WINNT=0x0A00
    /DNOMINMAX
    /DUNICODE
    /D_UNICODE
    /permissive-
    /Zc:__cplusplus
    /utf-8
)

pybind11_add_module(dds_pybind MODULE dds_pybind.cpp ${DIRECTX_TEX_SOURCES} ${DIRECTX_TEX_HEADERS})

target_link_libraries(dds_pybind PRIVATE Python3::Module pybind11::module)

target_link_options(dds_pybind PRIVATE "/EXPORT:PyInit_dds_pybind")

set_target_properties(dds_pybind PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_LIBRARY_OUTPUT_DIRECTORY}"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_LIBRARY_OUTPUT_DIRECTORY}"
    PDB_OUTPUT_DIRECTORY "${CMAKE_LIBRARY_OUTPUT_DIRECTORY}"
)
