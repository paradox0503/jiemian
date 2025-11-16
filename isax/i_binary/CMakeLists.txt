cmake_minimum_required(VERSION 3.16)
project(bsax)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}  -mavx2")

file(GLOB IBINARY_LIB_SRC   # 把文件打包
        ./*.cpp
        ./*.h)

include_directories(../sax/include)
include_directories(../util)

add_library(i_binary SHARED ${IBINARY_LIB_SRC})