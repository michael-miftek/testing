@echo off
@echo Cleaning Libcytospectrum

set PROJ_DIR=%~dp0

@echo Checking for build directory and removing
if exist %PROJ_DIR%libcytospectrum\build\ (
    cd %PROJ_DIR%libcytospectrum\build\
    cmake --build . --target clean
    cd ..
    rm -rf %PROJ_DIR%libcytospectrum\build\
)
else (
    goto end
)

@echo Checking for lib directory and removing
if exist %PROJ_DIR%lib (
    rm -rf %PROJ_DIR%lib
)
else(
    goto end
)

:end
@echo Finished Cleaning

