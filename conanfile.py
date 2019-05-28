# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class LibnameConan(ConanFile):
    name = "vulkan_validation_layers"
    version = "1.1.106"
    description = "Vulkan Validation Layers"
    topics = ("conan", "vulkan", "validation", "layer", "debug", )
    url = "https://github.com/bincrafters/conan-vulkan_validation_layers"
    homepage = "https://github.com/KhronosGroup/Vulkan-ValidationLayers"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "Apache-2.0"
    exports = ["LICENSE.md", ]
    no_copy_source = True
    exports_sources = ["CMakeLists.txt", ]
    generators = "cmake",

    settings = "os", "arch", "compiler", "build_type"

    _source_subfolder = "source_subfolder"

    def build_requirements(self):
        self.build_requires("glslang/7.11.3214@{}/{}".format(self.user, self.channel))
        self.build_requires("vulkan_headers/{}@{}/{}".format(self.version, self.user, self.channel))
        # self.build_requires("vulkan_loader/{}@{}/{}".format(self.version, self.user, self.channel))
        self.build_requires("spirv_tools/2019.3@{}/{}".format(self.user, self.channel))

    def requirements(self):
        self.requires("vulkan_loader/{}@{}/{}".format(self.version, self.user, self.channel))

    def source(self):
        source_url = "https://github.com/KhronosGroup/Vulkan-ValidationLayers/archive/v{}.tar.gz".format(self.version)
        sha256 = "e095e7c23fe52098e966c056d3e9684d6b915f129d736556bc5a33e9574bd735"
        tools.get(source_url, sha256=sha256)
        os.rename("Vulkan-ValidationLayers-{}".format(self.version), self._source_subfolder)

    def _safe_vulkan_loader_option(self, option):
        if option in self.options["vulkan_loader"].fields:
            return getattr(self.options["vulkan_loader"], option)
        return False

    def build(self):
        cmake = CMake(self)
        cmake_defines = {
            "GLSLANG_INSTALL_DIR": self.deps_cpp_info["glslang"].rootpath,
            "VULKAN_HEADERS_INSTALL_DIR": self.deps_cpp_info["vulkan_headers"].rootpath,
            "VULKAN_LOADER_INSTALL_DIR": self.deps_cpp_info["vulkan_loader"].rootpath,
            "BUILD_WSI_WAYLAND_SUPPORT": self._safe_vulkan_loader_option("wayland"),
            "BUILD_WSI_XCB_SUPPORT": self._safe_vulkan_loader_option("xcb"),
            "BUILD_WSI_XLIB_SUPPORT": self._safe_vulkan_loader_option("xlib"),
        }
        cmake.configure(defs=cmake_defines)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install(build_dir=self.build_folder)

        self.copy(pattern="LICENSE.txt", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        layer_manifest_path = os.path.join(self.package_folder, "share", "vulkan", "explicit_layer.d")
        self.user_info.LAYER_MANIFEST_PATH = layer_manifest_path

        self.output.info("Appending VK_LAYER_PATH environment variable: {}".format(layer_manifest_path))
        self.env_info.VK_LAYER_PATH.append(layer_manifest_path)
