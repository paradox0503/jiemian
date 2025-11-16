cmake_minimum_required(VERSION 3.23)
project(bsax)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}  -mavx2 -pthread -fopenmp")
FIND_PACKAGE( OpenMP REQUIRED)
if (OPENMP_FOUND)
    message("OPENMP FOUND")
endif()
add_compile_options(-fopenmp)

# 给之后所有声明executable和library都能用include内的.h文件
include_directories(./sax/include)
include_directories(./util)

add_subdirectory(sax)   # 添加子目录sax,运行子目录的cmake,拿到子目录声明的sax
add_subdirectory(util)
add_subdirectory(i_binary)

# add_executable(test_sax test_sax.cpp)
# target_link_libraries(test_sax sax)

# add_executable(test_isax test/test_isax.cpp)
add_executable(approx_isax test/approximate_search.cpp)
add_executable(exact_isax test/exact_search.cpp)
target_link_libraries(approx_isax i_binary sax util tcmalloc)
target_link_libraries(exact_isax i_binary sax util tcmalloc)

