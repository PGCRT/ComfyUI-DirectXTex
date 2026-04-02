#define PYBIND11_EXPORT
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include <DirectXTex.h>
#include <vector>
#include <string>
#include <cstring>
#include <algorithm>

namespace py = pybind11;

static const std::vector<std::pair<const char*, DXGI_FORMAT>> FORMAT_MAP = {
    {"DXGI_FORMAT_UNKNOWN", DXGI_FORMAT_UNKNOWN},
    {"DXGI_FORMAT_R32G32B32A32_TYPELESS", DXGI_FORMAT_R32G32B32A32_TYPELESS},
    {"DXGI_FORMAT_R32G32B32A32_FLOAT", DXGI_FORMAT_R32G32B32A32_FLOAT},
    {"DXGI_FORMAT_R32G32B32A32_UINT", DXGI_FORMAT_R32G32B32A32_UINT},
    {"DXGI_FORMAT_R32G32B32A32_SINT", DXGI_FORMAT_R32G32B32A32_SINT},
    {"DXGI_FORMAT_R32G32B32_TYPELESS", DXGI_FORMAT_R32G32B32_TYPELESS},
    {"DXGI_FORMAT_R32G32B32_FLOAT", DXGI_FORMAT_R32G32B32_FLOAT},
    {"DXGI_FORMAT_R32G32B32_UINT", DXGI_FORMAT_R32G32B32_UINT},
    {"DXGI_FORMAT_R32G32B32_SINT", DXGI_FORMAT_R32G32B32_SINT},
    {"DXGI_FORMAT_R16G16B16A16_TYPELESS", DXGI_FORMAT_R16G16B16A16_TYPELESS},
    {"DXGI_FORMAT_R16G16B16A16_FLOAT", DXGI_FORMAT_R16G16B16A16_FLOAT},
    {"DXGI_FORMAT_R16G16B16A16_UNORM", DXGI_FORMAT_R16G16B16A16_UNORM},
    {"DXGI_FORMAT_R16G16B16A16_UINT", DXGI_FORMAT_R16G16B16A16_UINT},
    {"DXGI_FORMAT_R16G16B16A16_SNORM", DXGI_FORMAT_R16G16B16A16_SNORM},
    {"DXGI_FORMAT_R16G16B16A16_SINT", DXGI_FORMAT_R16G16B16A16_SINT},
    {"DXGI_FORMAT_R32G32_TYPELESS", DXGI_FORMAT_R32G32_TYPELESS},
    {"DXGI_FORMAT_R32G32_FLOAT", DXGI_FORMAT_R32G32_FLOAT},
    {"DXGI_FORMAT_R32G32_UINT", DXGI_FORMAT_R32G32_UINT},
    {"DXGI_FORMAT_R32G32_SINT", DXGI_FORMAT_R32G32_SINT},
    {"DXGI_FORMAT_R10G10B10A2_TYPELESS", DXGI_FORMAT_R10G10B10A2_TYPELESS},
    {"DXGI_FORMAT_R10G10B10A2_UNORM", DXGI_FORMAT_R10G10B10A2_UNORM},
    {"DXGI_FORMAT_R10G10B10A2_UINT", DXGI_FORMAT_R10G10B10A2_UINT},
    {"DXGI_FORMAT_R11G11B10_FLOAT", DXGI_FORMAT_R11G11B10_FLOAT},
    {"DXGI_FORMAT_R8G8B8A8_TYPELESS", DXGI_FORMAT_R8G8B8A8_TYPELESS},
    {"DXGI_FORMAT_R8G8B8A8_UNORM", DXGI_FORMAT_R8G8B8A8_UNORM},
    {"DXGI_FORMAT_R8G8B8A8_UNORM_SRGB", DXGI_FORMAT_R8G8B8A8_UNORM_SRGB},
    {"DXGI_FORMAT_R8G8B8A8_UINT", DXGI_FORMAT_R8G8B8A8_UINT},
    {"DXGI_FORMAT_R8G8B8A8_SNORM", DXGI_FORMAT_R8G8B8A8_SNORM},
    {"DXGI_FORMAT_R8G8B8A8_SINT", DXGI_FORMAT_R8G8B8A8_SINT},
    {"DXGI_FORMAT_R16G16_TYPELESS", DXGI_FORMAT_R16G16_TYPELESS},
    {"DXGI_FORMAT_R16G16_FLOAT", DXGI_FORMAT_R16G16_FLOAT},
    {"DXGI_FORMAT_R16G16_UNORM", DXGI_FORMAT_R16G16_UNORM},
    {"DXGI_FORMAT_R16G16_UINT", DXGI_FORMAT_R16G16_UINT},
    {"DXGI_FORMAT_R16G16_SNORM", DXGI_FORMAT_R16G16_SNORM},
    {"DXGI_FORMAT_R16G16_SINT", DXGI_FORMAT_R16G16_SINT},
    {"DXGI_FORMAT_R32_TYPELESS", DXGI_FORMAT_R32_TYPELESS},
    {"DXGI_FORMAT_D32_FLOAT", DXGI_FORMAT_D32_FLOAT},
    {"DXGI_FORMAT_R32_FLOAT", DXGI_FORMAT_R32_FLOAT},
    {"DXGI_FORMAT_R32_UINT", DXGI_FORMAT_R32_UINT},
    {"DXGI_FORMAT_R32_SINT", DXGI_FORMAT_R32_SINT},
    {"DXGI_FORMAT_R8G8_TYPELESS", DXGI_FORMAT_R8G8_TYPELESS},
    {"DXGI_FORMAT_R8G8_UNORM", DXGI_FORMAT_R8G8_UNORM},
    {"DXGI_FORMAT_R8G8_UINT", DXGI_FORMAT_R8G8_UINT},
    {"DXGI_FORMAT_R8G8_SNORM", DXGI_FORMAT_R8G8_SNORM},
    {"DXGI_FORMAT_R8G8_SINT", DXGI_FORMAT_R8G8_SINT},
    {"DXGI_FORMAT_R16_TYPELESS", DXGI_FORMAT_R16_TYPELESS},
    {"DXGI_FORMAT_R16_FLOAT", DXGI_FORMAT_R16_FLOAT},
    {"DXGI_FORMAT_D16_UNORM", DXGI_FORMAT_D16_UNORM},
    {"DXGI_FORMAT_R16_UNORM", DXGI_FORMAT_R16_UNORM},
    {"DXGI_FORMAT_R16_UINT", DXGI_FORMAT_R16_UINT},
    {"DXGI_FORMAT_R16_SNORM", DXGI_FORMAT_R16_SNORM},
    {"DXGI_FORMAT_R16_SINT", DXGI_FORMAT_R16_SINT},
    {"DXGI_FORMAT_R8_TYPELESS", DXGI_FORMAT_R8_TYPELESS},
    {"DXGI_FORMAT_R8_UNORM", DXGI_FORMAT_R8_UNORM},
    {"DXGI_FORMAT_R8_UINT", DXGI_FORMAT_R8_UINT},
    {"DXGI_FORMAT_R8_SNORM", DXGI_FORMAT_R8_SNORM},
    {"DXGI_FORMAT_R8_SINT", DXGI_FORMAT_R8_SINT},
    {"DXGI_FORMAT_R8G8_B8G8_UNORM", DXGI_FORMAT_R8G8_B8G8_UNORM},
    {"DXGI_FORMAT_G8R8_G8B8_UNORM", DXGI_FORMAT_G8R8_G8B8_UNORM},
    {"DXGI_FORMAT_B8G8R8A8_UNORM", DXGI_FORMAT_B8G8R8A8_UNORM},
    {"DXGI_FORMAT_B8G8R8X8_UNORM", DXGI_FORMAT_B8G8R8X8_UNORM},
    {"DXGI_FORMAT_B8G8R8A8_UNORM_SRGB", DXGI_FORMAT_B8G8R8A8_UNORM_SRGB},
    {"DXGI_FORMAT_B8G8R8X8_UNORM_SRGB", DXGI_FORMAT_B8G8R8X8_UNORM_SRGB},
    {"DXGI_FORMAT_BC1_TYPELESS", DXGI_FORMAT_BC1_TYPELESS},
    {"DXGI_FORMAT_BC1_UNORM", DXGI_FORMAT_BC1_UNORM},
    {"DXGI_FORMAT_BC1_UNORM_SRGB", DXGI_FORMAT_BC1_UNORM_SRGB},
    {"DXGI_FORMAT_BC2_TYPELESS", DXGI_FORMAT_BC2_TYPELESS},
    {"DXGI_FORMAT_BC2_UNORM", DXGI_FORMAT_BC2_UNORM},
    {"DXGI_FORMAT_BC2_UNORM_SRGB", DXGI_FORMAT_BC2_UNORM_SRGB},
    {"DXGI_FORMAT_BC3_TYPELESS", DXGI_FORMAT_BC3_TYPELESS},
    {"DXGI_FORMAT_BC3_UNORM", DXGI_FORMAT_BC3_UNORM},
    {"DXGI_FORMAT_BC3_UNORM_SRGB", DXGI_FORMAT_BC3_UNORM_SRGB},
    {"DXGI_FORMAT_BC4_TYPELESS", DXGI_FORMAT_BC4_TYPELESS},
    {"DXGI_FORMAT_BC4_UNORM", DXGI_FORMAT_BC4_UNORM},
    {"DXGI_FORMAT_BC4_SNORM", DXGI_FORMAT_BC4_SNORM},
    {"DXGI_FORMAT_BC5_TYPELESS", DXGI_FORMAT_BC5_TYPELESS},
    {"DXGI_FORMAT_BC5_UNORM", DXGI_FORMAT_BC5_UNORM},
    {"DXGI_FORMAT_BC5_SNORM", DXGI_FORMAT_BC5_SNORM},
    {"DXGI_FORMAT_BC6H_TYPELESS", DXGI_FORMAT_BC6H_TYPELESS},
    {"DXGI_FORMAT_BC6H_UF16", DXGI_FORMAT_BC6H_UF16},
    {"DXGI_FORMAT_BC6H_SF16", DXGI_FORMAT_BC6H_SF16},
    {"DXGI_FORMAT_BC7_TYPELESS", DXGI_FORMAT_BC7_TYPELESS},
    {"DXGI_FORMAT_BC7_UNORM", DXGI_FORMAT_BC7_UNORM},
    {"DXGI_FORMAT_BC7_UNORM_SRGB", DXGI_FORMAT_BC7_UNORM_SRGB},
    {"DXGI_FORMAT_B5G6R5_UNORM", DXGI_FORMAT_B5G6R5_UNORM},
    {"DXGI_FORMAT_B5G5R5A1_UNORM", DXGI_FORMAT_B5G5R5A1_UNORM},
    {"DXGI_FORMAT_B4G4R4A4_UNORM", DXGI_FORMAT_B4G4R4A4_UNORM},
};

static const std::vector<std::pair<const char*, DXGI_FORMAT>> LEGACY_FORMAT_MAP = {
    {"DXT1", DXGI_FORMAT_BC1_UNORM},
    {"DXT2", DXGI_FORMAT_BC2_UNORM},
    {"DXT3", DXGI_FORMAT_BC2_UNORM},
    {"DXT4", DXGI_FORMAT_BC3_UNORM},
    {"DXT5", DXGI_FORMAT_BC3_UNORM},
    {"ATI1", DXGI_FORMAT_BC4_UNORM},
    {"BC4U", DXGI_FORMAT_BC4_UNORM},
    {"BC4S", DXGI_FORMAT_BC4_SNORM},
    {"ATI2", DXGI_FORMAT_BC5_UNORM},
    {"BC5U", DXGI_FORMAT_BC5_UNORM},
    {"BC5S", DXGI_FORMAT_BC5_SNORM},
    {"RGBG", DXGI_FORMAT_R8G8_B8G8_UNORM},
    {"GRGB", DXGI_FORMAT_G8R8_G8B8_UNORM},
    {"YUY2", DXGI_FORMAT_YUY2},
};

int string_to_dxgi_format(const std::string& fmt) {
    for (const auto& pair : FORMAT_MAP) {
        if (strcmp(pair.first, fmt.c_str()) == 0) {
            return static_cast<int>(pair.second);
        }
    }
    for (const auto& pair : LEGACY_FORMAT_MAP) {
        if (strcmp(pair.first, fmt.c_str()) == 0) {
            return static_cast<int>(pair.second);
        }
    }
    return static_cast<int>(DXGI_FORMAT_UNKNOWN);
}

std::string dxgi_format_to_string(int fmt) {
    for (const auto& pair : FORMAT_MAP) {
        if (pair.second == static_cast<DXGI_FORMAT>(fmt)) {
            return std::string(pair.first);
        }
    }
    for (const auto& pair : LEGACY_FORMAT_MAP) {
        if (pair.second == static_cast<DXGI_FORMAT>(fmt)) {
            return std::string(pair.first);
        }
    }
    return "DXGI_FORMAT_UNKNOWN";
}

py::tuple load_dds_from_memory(py::bytes data) {
    DirectX::ScratchImage scratch;
    DirectX::TexMetadata metadata;
    
    std::string data_str = data.cast<std::string>();
    const uint8_t* bytes = reinterpret_cast<const uint8_t*>(data_str.data());
    size_t size = data_str.size();
    
    HRESULT hr = DirectX::GetMetadataFromDDSMemory(bytes, size, DirectX::DDS_FLAGS_NONE, metadata);
    if (FAILED(hr)) {
        throw py::value_error("Failed to get DDS metadata: " + std::to_string(hr));
    }
    
    hr = DirectX::LoadFromDDSMemory(bytes, size, DirectX::DDS_FLAGS_NONE, &metadata, scratch);
    if (FAILED(hr)) {
        throw py::value_error("Failed to load DDS: " + std::to_string(hr));
    }
    
    DXGI_FORMAT outputFormat = DXGI_FORMAT_R8G8B8A8_UNORM;
    bool needsDecompress = DirectX::IsCompressed(metadata.format);
    bool needsConvert = metadata.format != outputFormat;
    
    DirectX::ScratchImage* outputImage = &scratch;
    DirectX::ScratchImage decompressed;
    
    if (needsDecompress) {
        hr = DirectX::Decompress(scratch.GetImages(), scratch.GetImageCount(), metadata, outputFormat, decompressed);
        if (FAILED(hr)) {
            throw py::value_error("Failed to decompress DDS: " + std::to_string(hr));
        }
        outputImage = &decompressed;
        metadata.format = outputFormat;
    } else if (needsConvert) {
        hr = DirectX::Convert(scratch.GetImages(), scratch.GetImageCount(), metadata, outputFormat, DirectX::TEX_FILTER_DEFAULT, 0.5f, decompressed);
        if (FAILED(hr)) {
            throw py::value_error("Failed to convert DDS: " + std::to_string(hr));
        }
        outputImage = &decompressed;
        metadata.format = outputFormat;
    }
    
    const DirectX::Image* img = outputImage->GetImages();
    size_t width = img->width;
    size_t height = img->height;
    size_t rowPitch = img->rowPitch;
    size_t slicePitch = img->slicePitch;
    
    std::vector<uint8_t> rgbaData(slicePitch);
    std::memcpy(rgbaData.data(), img->pixels, std::min(slicePitch, rowPitch * height));
    
    py::array_t<uint8_t> result(std::vector<py::ssize_t>{static_cast<py::ssize_t>(height), static_cast<py::ssize_t>(width), 4});
    auto buf = result.request();
    uint8_t* ptr = static_cast<uint8_t*>(buf.ptr);
    
    if (rowPitch == width * 4) {
        std::memcpy(ptr, rgbaData.data(), slicePitch);
    } else {
        for (size_t y = 0; y < height; y++) {
            std::memcpy(ptr + y * width * 4, rgbaData.data() + y * rowPitch, width * 4);
        }
    }
    
    std::string formatStr = dxgi_format_to_string(img->format);
    
    return py::make_tuple(result, formatStr, static_cast<py::ssize_t>(width), static_cast<py::ssize_t>(height));
}

py::bytes save_dds_to_memory(py::array_t<uint8_t>& image, const std::string& formatStr, bool generateMips) {
    auto buf = image.request();
    
    if (buf.ndim != 3) {
        throw py::value_error("Image must be 3D array (H, W, C)");
    }
    
    if (buf.shape[2] != 4) {
        throw py::value_error("Image must have 4 channels");
    }
    
    size_t height = buf.shape[0];
    size_t width = buf.shape[1];
    
    DXGI_FORMAT format = static_cast<DXGI_FORMAT>(string_to_dxgi_format(formatStr));
    if (format == DXGI_FORMAT_UNKNOWN) {
        throw py::value_error("Unknown format: " + formatStr);
    }
    
    bool isCompressed = DirectX::IsCompressed(format);
    
    DirectX::TexMetadata metadata;
    metadata.width = width;
    metadata.height = height;
    metadata.depth = 1;
    metadata.arraySize = 1;
    metadata.mipLevels = 1;
    metadata.miscFlags = 0;
    metadata.miscFlags2 = 0;
    metadata.format = isCompressed ? DXGI_FORMAT_R8G8B8A8_UNORM : format;
    metadata.dimension = DirectX::TEX_DIMENSION_TEXTURE2D;
    
    DirectX::ScratchImage scratch;
    HRESULT hr = scratch.Initialize2D(metadata.format, width, height, 1, 1, DirectX::CP_FLAGS_NONE);
    if (FAILED(hr)) {
        throw py::value_error("Failed to initialize scratch image: " + std::to_string(hr));
    }
    
    const DirectX::Image* srcImg = scratch.GetImages();
    DirectX::Image imgCopy = *srcImg;
    imgCopy.width = width;
    imgCopy.height = height;
    imgCopy.format = metadata.format;
    imgCopy.rowPitch = width * 4;
    imgCopy.slicePitch = width * height * 4;
    
    uint8_t* destPixels = imgCopy.pixels;
    uint8_t* srcPixels = static_cast<uint8_t*>(buf.ptr);
    
    for (size_t y = 0; y < height; y++) {
        std::memcpy(destPixels + y * width * 4, srcPixels + y * width * 4, width * 4);
    }
    
    DirectX::ScratchImage compressed;
    if (isCompressed) {
        DirectX::TEX_COMPRESS_FLAGS compressFlags = DirectX::TEX_COMPRESS_DEFAULT;
        if (format == DXGI_FORMAT_BC7_UNORM || format == DXGI_FORMAT_BC7_UNORM_SRGB) {
            compressFlags = static_cast<DirectX::TEX_COMPRESS_FLAGS>(DirectX::TEX_COMPRESS_BC7_QUICK);
        }
        hr = DirectX::Compress(scratch.GetImages(), scratch.GetImageCount(), metadata, format, compressFlags, 0.5f, compressed);
        if (FAILED(hr)) {
            throw py::value_error("Failed to compress image: " + std::to_string(hr));
        }
    } else {
        compressed = std::move(scratch);
    }
    
    DirectX::Blob blob;
    const DirectX::Image* finalImg = compressed.GetImages();
    hr = DirectX::SaveToDDSMemory(finalImg, 1, compressed.GetMetadata(), DirectX::DDS_FLAGS_NONE, blob);
    if (FAILED(hr)) {
        throw py::value_error("Failed to save DDS: " + std::to_string(hr));
    }
    
    std::string result(reinterpret_cast<const char*>(blob.GetBufferPointer()), blob.GetBufferSize());
    return py::bytes(result);
}

std::string get_dds_format_from_memory(py::bytes data) {
    DirectX::TexMetadata metadata;
    
    std::string data_str = data.cast<std::string>();
    const uint8_t* bytes = reinterpret_cast<const uint8_t*>(data_str.data());
    size_t size = data_str.size();
    
    HRESULT hr = DirectX::GetMetadataFromDDSMemory(bytes, size, DirectX::DDS_FLAGS_NONE, metadata);
    if (FAILED(hr)) {
        return "DXGI_FORMAT_UNKNOWN";
    }
    
    return dxgi_format_to_string(metadata.format);
}

std::vector<std::string> get_supported_formats() {
    std::vector<std::string> formats;
    for (const auto& pair : FORMAT_MAP) {
        formats.push_back(std::string(pair.first));
    }
    for (const auto& pair : LEGACY_FORMAT_MAP) {
        formats.push_back(std::string(pair.first));
    }
    return formats;
}

PYBIND11_MODULE(dds_pybind, m) {
    m.def("load_dds_from_memory", &load_dds_from_memory, "Load DDS from memory",
          py::return_value_policy::take_ownership);
    m.def("save_dds_to_memory", &save_dds_to_memory, "Save DDS to memory",
          py::return_value_policy::take_ownership);
    m.def("get_dds_format_from_memory", &get_dds_format_from_memory, "Get DDS format without loading image");
    m.def("get_supported_formats", &get_supported_formats, "Get list of supported formats");
    m.def("string_to_dxgi_format", &string_to_dxgi_format, "Convert string to DXGI format");
    m.def("dxgi_format_to_string", &dxgi_format_to_string, "Convert DXGI format to string");
}
