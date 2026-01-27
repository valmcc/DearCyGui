# PowerShell script to build DearCyGui locally on Windows
# This script builds for your current Python installation only (simpler, faster for development)

param(
    [switch]$Clean,
    [switch]$SkipDependencies,
    [switch]$Install
)

Write-Host "=== DearCyGui Local Windows Builder ===" -ForegroundColor Cyan
Write-Host ""

# Check if running with administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin -and -not $SkipDependencies) {
    Write-Host "WARNING: Not running as administrator. Chocolatey installations may fail." -ForegroundColor Yellow
    Write-Host "Consider running PowerShell as Administrator or use -SkipDependencies flag." -ForegroundColor Yellow
    Write-Host ""
}

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Green
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or later from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Check if git submodules are initialized
Write-Host "Checking git submodules..." -ForegroundColor Green
if (-not (Test-Path "thirdparty/SDL/.git")) {
    Write-Host "Initializing git submodules..." -ForegroundColor Yellow
    git submodule update --init --recursive
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to initialize git submodules" -ForegroundColor Red
        exit 1
    }
}
Write-Host "Git submodules OK" -ForegroundColor Green
Write-Host ""

# Install system dependencies if not skipped
if (-not $SkipDependencies) {
    Write-Host "Installing system dependencies..." -ForegroundColor Green

    # Check if Chocolatey is installed
    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Host "Installing Chocolatey package manager..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

        # Refresh environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }

    Write-Host "Installing CMake..." -ForegroundColor Yellow
    choco install cmake -y --no-progress

    Write-Host "Installing Visual Studio Build Tools..." -ForegroundColor Yellow
    choco install visualstudio2022buildtools -y --no-progress --package-parameters "--add Microsoft.VisualStudio.Component.VC.Tools.x86.x64"

    Write-Host "Installing Windows SDK..." -ForegroundColor Yellow
    choco install windows-sdk-10.0 -y --no-progress

    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

    Write-Host "System dependencies installed successfully!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Skipping system dependencies installation (as requested)" -ForegroundColor Yellow
    Write-Host ""
}

# Clean build directories if requested
if ($Clean) {
    Write-Host "Cleaning previous build artifacts..." -ForegroundColor Yellow
    $dirsToClean = @("build", "build_SDL", "build_FT", "dist", "*.egg-info")
    foreach ($dir in $dirsToClean) {
        if (Test-Path $dir) {
            Remove-Item -Recurse -Force $dir
            Write-Host "  Removed: $dir" -ForegroundColor Gray
        }
    }
    Write-Host "Clean complete" -ForegroundColor Green
    Write-Host ""
}

# Upgrade pip and install Python build dependencies
Write-Host "Installing Python build dependencies..." -ForegroundColor Green
python -m pip install --upgrade pip
python -m pip install "Cython==3.1.6" wheel setuptools cmake build

# Create temp directory
$tempDir = "C:\temp"
if (-not (Test-Path $tempDir)) {
    Write-Host "Creating temp directory: $tempDir" -ForegroundColor Green
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
}

# Set environment variables for build
$env:TEMP = $tempDir
$env:TMP = $tempDir
$env:TMPDIR = $tempDir

Write-Host ""
Write-Host "=== Starting build ===" -ForegroundColor Cyan
Write-Host ""

# Build the package
if ($Install) {
    Write-Host "Building and installing package..." -ForegroundColor Green
    python -m pip install -e .
} else {
    Write-Host "Building wheel..." -ForegroundColor Green
    python -m build --wheel
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Build completed successfully! ===" -ForegroundColor Green

    if ($Install) {
        Write-Host "Package installed in development mode" -ForegroundColor Green
        Write-Host "You can now import dearcygui in Python" -ForegroundColor Cyan
    } else {
        Write-Host "Wheel is available in: dist/" -ForegroundColor Green
        Write-Host ""
        Write-Host "Built wheels:" -ForegroundColor Cyan
        Get-ChildItem -Path "dist" -Filter "*.whl" | ForEach-Object {
            Write-Host "  - $($_.Name)" -ForegroundColor White
        }
        Write-Host ""
        Write-Host "To install the wheel, run:" -ForegroundColor Cyan
        $wheelFile = (Get-ChildItem -Path "dist" -Filter "*.whl" | Select-Object -First 1).Name
        if ($wheelFile) {
            Write-Host "  pip install dist\$wheelFile" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host ""
    Write-Host "=== Build failed! ===" -ForegroundColor Red
    Write-Host "Check the error messages above for details" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=== Build script completed ===" -ForegroundColor Cyan
