# PowerShell script to build Windows wheels using cibuildwheel (similar to CI)
# This script builds wheels for multiple Python versions

param(
    [string]$OutputDir = ".\wheelhouse",
    [string]$PythonVersions = "cp310-win_amd64 cp311-win_amd64 cp312-win_amd64 cp313-win_amd64 cp313t-win_amd64 cp314-win_amd64 cp314t-win_amd64",
    [switch]$SkipDependencies
)

Write-Host "=== DearCyGui Windows Wheel Builder (cibuildwheel) ===" -ForegroundColor Cyan
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

# Upgrade pip and install Python build dependencies
Write-Host "Installing Python build dependencies..." -ForegroundColor Green
python -m pip install --upgrade pip
python -m pip install cibuildwheel

# Create output directory
Write-Host "Creating output directory: $OutputDir" -ForegroundColor Green
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

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
$env:CIBW_BUILD = $PythonVersions
$env:CIBW_ENABLE = "cpython-freethreading pypy"
$env:CIBW_ENVIRONMENT = "TEMP=C:\temp TMP=C:\temp TMPDIR=C:\temp"
$env:CIBW_BEFORE_BUILD = "IF NOT EXIST C:\temp mkdir C:\temp"
$env:CIBW_BUILD_FRONTEND = "build"

Write-Host ""
Write-Host "=== Starting wheel build ===" -ForegroundColor Cyan
Write-Host "Output directory: $OutputDir" -ForegroundColor Cyan
Write-Host "Python versions: $PythonVersions" -ForegroundColor Cyan
Write-Host ""

# Build wheels
$absOutputDir = (Resolve-Path $OutputDir).Path
python -m cibuildwheel --platform windows --output-dir $absOutputDir

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Build completed successfully! ===" -ForegroundColor Green
    Write-Host "Wheels are available in: $absOutputDir" -ForegroundColor Green
    Write-Host ""
    Write-Host "Built wheels:" -ForegroundColor Cyan
    Get-ChildItem -Path $absOutputDir -Filter "*.whl" | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor White
    }
} else {
    Write-Host ""
    Write-Host "=== Build failed! ===" -ForegroundColor Red
    exit 1
}
