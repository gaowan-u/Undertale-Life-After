cmake_minimum_required(VERSION 3.10)
project(MapBoundaryDetector)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找 OpenCV
find_package(OpenCV REQUIRED)

# 修复 Termux 头文件路径问题
include_directories(${OpenCV_INCLUDE_DIRS})
include_directories(/data/data/com.termux/files/usr/include)
include_directories(/data/data/com.termux/files/usr/include/opencv4)

# 查找 nlohmann/json
find_package(nlohmann_json QUIET)
if(NOT nlohmann_json_FOUND)
    message(STATUS "nlohmann_json not found, downloading...")
    include(FetchContent)
    FetchContent_Declare(
        json
        URL https://github.com/nlohmann/json/releases/download/v3.11.2/json.tar.xz
        DOWNLOAD_EXTRACT_TIMESTAMP TRUE
    )
    FetchContent_MakeAvailable(json)
endif()

add_executable(MapBoundaryDetector main.cpp)
target_link_libraries(MapBoundaryDetector ${OpenCV_LIBS} nlohmann_json::nlohmann_json)