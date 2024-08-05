cmake_minimum_required(VERSION 3.10)

# Project name and C++ standard
project(MasterService CXX)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Protobuf package
find_package(Protobuf REQUIRED)

# Define paths
set(PROTOBUF_DIR ${CMAKE_CURRENT_SOURCE_DIR}/protobuf)
set(SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)

# List all proto files
file(GLOB PROTO_FILES "${PROTOBUF_DIR}/*.proto")

# Generate C++ files from proto files
protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${PROTO_FILES})

# Add include directories
include_directories(${SRC_DIR} ${CMAKE_CURRENT_BINARY_DIR} ${Protobuf_INCLUDE_DIRS})

# Add the executable target
add_executable(MasterService
    ${SRC_DIR}/main.cc
    ${PROTO_SRCS}
    ${PROTO_HDRS}
)

# Link libraries
target_link_libraries(MasterService ${Protobuf_LIBRARIES} pthread)
