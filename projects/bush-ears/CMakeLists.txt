cmake_minimum_required(VERSION 3.20)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

# Use C++20 features (better compatibility)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Enable optimizations for audio processing
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG -march=native")

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

# Add our C++ module
pybind11_add_module(_core MODULE src/main.cpp)

# Link math library and enable vectorization
target_link_libraries(_core PRIVATE m)
target_compile_options(_core PRIVATE -ffast-math -ftree-vectorize)

install(TARGETS _core DESTINATION ${SKBUILD_PROJECT_NAME})
