# cmake_minimum_required(VERSION 3.16)
# project(dids)

# set(CMAKE_CXX_STANDARD 14)
# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}  -mavx2 -pthread -fopenmp")
# set(CMAKE_BUILD_TYPE Release)

# FIND_PACKAGE(OpenMP REQUIRED)
# add_compile_options(-fopenmp)

# add_executable(example example.cpp random_data.cpp)
# target_link_libraries(example tcmalloc gsl)


cmake_minimum_required(VERSION 3.16)
project(dids)

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 14)

# 添加编译选项
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mavx2 -pthread -fopenmp")

# 设置构建类型为 Release
set(CMAKE_BUILD_TYPE Release)

# 查找 OpenMP 并启用
find_package(OpenMP REQUIRED)
if (OpenMP_FOUND)
    add_compile_options(-fopenmp)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
endif()

# 添加 TCMalloc 库路径
link_directories(/usr/lib/x86_64-linux-gnu)

# 添加可执行文件
add_executable(index index.cpp random_data.cpp)
add_executable(search search.cpp random_data.cpp)

# 手动指定 TCMalloc 库文件路径
target_link_libraries(search
    /usr/lib/x86_64-linux-gnu/libtcmalloc_minimal.so.4  # 直接指定库文件路径
    gsl
    ${OpenMP_CXX_FLAGS}
)

target_link_libraries(index
    /usr/lib/x86_64-linux-gnu/libtcmalloc_minimal.so.4  # 直接指定库文件路径
    gsl
    ${OpenMP_CXX_FLAGS}
)
