cmake_minimum_required(VERSION 3.16)
project(evogen VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_compile_options(-Wall -Wextra -Wpedantic)

include(FetchContent)
FetchContent_Declare(
  json
  GIT_REPOSITORY https://github.com/nlohmann/json.git
  GIT_TAG v3.11.3
  GIT_SHALLOW TRUE
)
FetchContent_Declare(
  Catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG v3.5.4
  GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(json Catch2)

set(EVOGEN_CORE_SOURCES
  src/core/genome.cpp
  src/core/rng.cpp
  src/core/agent.cpp
  src/core/selection.cpp
  src/core/crossover.cpp
  src/core/mutation.cpp
  src/core/population.cpp
  src/core/experiment_config.cpp
  src/core/recorder.cpp
  src/core/generation_loop.cpp
  src/environments/function_approx_env.cpp
)

add_library(evogen_core ${EVOGEN_CORE_SOURCES})
target_include_directories(evogen_core PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/src")
target_link_libraries(evogen_core PUBLIC nlohmann_json::nlohmann_json)

add_executable(evogen src/main.cpp)
target_link_libraries(evogen PRIVATE evogen_core)
target_compile_definitions(evogen PRIVATE EVOGEN_VERSION="${PROJECT_VERSION}")

list(APPEND CMAKE_MODULE_PATH ${catch2_SOURCE_DIR}/extras)
enable_testing()
add_executable(evogen_tests
  tests/test_genome.cpp
  tests/test_agent.cpp
  tests/test_operators.cpp
  tests/test_config_loop.cpp
)
target_link_libraries(evogen_tests PRIVATE evogen_core Catch2::Catch2WithMain)
include(CTest)
include(Catch)
catch_discover_tests(evogen_tests
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)
