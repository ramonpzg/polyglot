cmake_minimum_required(VERSION 3.25)
project(numcrunch CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(pybind11 REQUIRED)

pybind11_add_module(_cpp_core
    src/cpp/mining_core.cpp
    src/cpp/python_bindings.cpp
)

target_include_directories(_cpp_core PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/cpp)

target_compile_features(_cpp_core PRIVATE cxx_std_23)
target_compile_options(_cpp_core PRIVATE
    $<$<CXX_COMPILER_ID:GNU,Clang>:-O3 -march=native -ffast-math>
    $<$<CXX_COMPILER_ID:MSVC>:/O2 /arch:AVX2>
)

