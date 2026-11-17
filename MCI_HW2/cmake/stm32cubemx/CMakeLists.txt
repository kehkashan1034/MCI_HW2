cmake_minimum_required(VERSION 3.22)

enable_language(C ASM)

# STM32 microcontroller definition
set(MX_Defines_Syms
    STM32F303xC
    $<$<CONFIG:Debug>:DEBUG>
)

# CMSIS include directories
set(MX_Include_Dirs
    ${CMAKE_CURRENT_SOURCE_DIR}/../../Core/Inc
    ${CMAKE_CURRENT_SOURCE_DIR}/../../Drivers/CMSIS/Device/ST/STM32F3xx/Include
    ${CMAKE_CURRENT_SOURCE_DIR}/../../Drivers/CMSIS/Include
)

# Application source files
set(MX_Application_Src
    ${CMAKE_CURRENT_SOURCE_DIR}/../../Core/Src/main.c
    ${CMAKE_CURRENT_SOURCE_DIR}/../../Core/Src/stm32f3xx_it.c
    ${CMAKE_CURRENT_SOURCE_DIR}/../../Core/Src/sysmem.c
    ${CMAKE_CURRENT_SOURCE_DIR}/../../Core/Src/syscalls.c
    ${CMAKE_CURRENT_SOURCE_DIR}/../../startup_stm32f303xc.s
)

# CMSIS system source
set(STM32_Drivers_Src
    ${CMAKE_CURRENT_SOURCE_DIR}/../../Core/Src/system_stm32f3xx.c
)

# Include paths and microcontroller definitions
add_library(stm32cubemx INTERFACE)

target_include_directories(stm32cubemx INTERFACE
    ${MX_Include_Dirs}
)

target_compile_definitions(stm32cubemx INTERFACE
    ${MX_Defines_Syms}
)

# CMSIS system library
add_library(STM32_Drivers OBJECT)

target_sources(STM32_Drivers PRIVATE
    ${STM32_Drivers_Src}
)

target_link_libraries(STM32_Drivers PUBLIC
    stm32cubemx
)

# Add application source files
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    ${MX_Application_Src}
)

# Link CMSIS system library
target_link_libraries(${CMAKE_PROJECT_NAME}
    STM32_Drivers
)

# Clean generated map file
set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES
    ADDITIONAL_CLEAN_FILES ${CMAKE_PROJECT_NAME}.map
)