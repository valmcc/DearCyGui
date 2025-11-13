@echo off
REM Batch script to build DearCyGui locally on Windows
REM This is a simpler wrapper that calls the PowerShell script

setlocal

echo.
echo === DearCyGui Windows Build Script ===
echo.
echo This script will build DearCyGui for your current Python installation.
echo.
echo Options:
echo   build_windows_local.bat              - Build wheel in dist/
echo   build_windows_local.bat clean        - Clean previous build and rebuild
echo   build_windows_local.bat install      - Build and install in development mode
echo   build_windows_local.bat skip-deps    - Skip system dependency installation
echo.

REM Parse command line arguments
set CLEAN_FLAG=
set INSTALL_FLAG=
set SKIP_DEPS_FLAG=

:parse_args
if "%1"=="" goto end_parse_args
if /i "%1"=="clean" set CLEAN_FLAG=-Clean
if /i "%1"=="install" set INSTALL_FLAG=-Install
if /i "%1"=="skip-deps" set SKIP_DEPS_FLAG=-SkipDependencies
shift
goto parse_args
:end_parse_args

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PowerShell is not available
    echo Please install PowerShell or use the PowerShell script directly
    exit /b 1
)

REM Run the PowerShell script
echo Starting PowerShell build script...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0build_windows_local.ps1" %CLEAN_FLAG% %INSTALL_FLAG% %SKIP_DEPS_FLAG%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build script completed successfully!
) else (
    echo.
    echo Build script failed!
    exit /b 1
)

endlocal
