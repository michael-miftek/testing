@echo off
@echo Building Libcytospectrum

set PROJ_DIR=%~dp0

if exist %PROJ_DIR%libcytospectrum\build\Release (
    rem file exists
) else ( 
    mkdir %PROJ_DIR%libcytospectrum\build\Release\
)
set RELEASE_DIR=%PROJ_DIR%libcytospectrum\build\Release\
echo Rlease Dir: %RELEASE_DIR%

rem @echo run vstudio prompt
cd %PROJ_DIR%libcytospectrum\build
rem @echo %~dp0
cmake ..
cmake --build .

rem cd %RELEASE_DIR%
rem @echo %~dp0
cmake -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release

cd %PROJ_DIR%

if not exist %PROJ_DIR%lib (
    mkdir %PROJ_DIR%lib
)

copy %RELEASE_DIR% %PROJ_DIR%lib
copy %PROJ_DIR%bin\ftd3xx\x64\*.* %PROJ_DIR%lib

set LIBCYTOSPECTRUM_PATH=%PROJ_DIR%lib
@echo %LIBCYTOSPECTRUM_PATH%

rem goto end
rem :end