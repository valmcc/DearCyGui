# Building DearCyGui on Windows

This guide explains how to build DearCyGui wheels locally on a Windows PC.

## Prerequisites

### Required Software

1. **Python 3.10 or later**
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Git**
   - Download from: https://git-scm.com/download/win
   - Required for cloning the repository and managing submodules

3. **Visual Studio Build Tools** (will be installed automatically by scripts)
   - Required for compiling C++ extensions
   - The scripts will install this via Chocolatey if not present

4. **CMake** (will be installed automatically by scripts)
   - Required for building SDL3 and FreeType dependencies
   - The scripts will install this via Chocolatey if not present

### System Requirements

- Windows 10 or later (64-bit)
- At least 4 GB of free disk space for build artifacts
- Administrator privileges (for installing dependencies)

## Build Methods

There are two main approaches to building DearCyGui on Windows:

### Method 1: Local Development Build (Recommended for Development)

This method builds a wheel for your current Python installation only. It's faster and simpler, ideal for development and testing.

#### Using PowerShell (Recommended)

```powershell
# Basic build (creates wheel in dist/)
.\build_windows_local.ps1

# Clean build (removes previous artifacts first)
.\build_windows_local.ps1 -Clean

# Build and install in development mode
.\build_windows_local.ps1 -Install

# Skip system dependencies (if already installed)
.\build_windows_local.ps1 -SkipDependencies
```

#### Using Command Prompt (cmd.exe)

```batch
REM Basic build
build_windows_local.bat

REM Clean build
build_windows_local.bat clean

REM Build and install
build_windows_local.bat install

REM Skip dependencies
build_windows_local.bat skip-deps
```

**Note:** You may need to run PowerShell as Administrator for the first build to install system dependencies.

### Method 2: Multi-Version Build with cibuildwheel (Recommended for Distribution)

This method builds wheels for multiple Python versions (3.10, 3.11, 3.12, 3.13, 3.14), similar to the CI pipeline. Use this when you want to create wheels for distribution.

```powershell
# Build wheels for all supported Python versions
.\build_windows_wheels_cibuildwheel.ps1

# Build wheels for specific Python versions
.\build_windows_wheels_cibuildwheel.ps1 -PythonVersions "cp312-win_amd64 cp313-win_amd64"

# Specify custom output directory
.\build_windows_wheels_cibuildwheel.ps1 -OutputDir "C:\my_wheels"

# Skip system dependencies (if already installed)
.\build_windows_wheels_cibuildwheel.ps1 -SkipDependencies
```

**Note:** This method requires cibuildwheel to install and manage multiple Python versions automatically.

## First-Time Setup

If this is your first time building DearCyGui on Windows:

1. **Clone the repository with submodules:**
   ```batch
   git clone --recursive https://github.com/valmcc/DearCyGui.git
   cd DearCyGui
   ```

2. **Run the build script as Administrator:**
   - Right-click on PowerShell and select "Run as Administrator"
   - Navigate to the DearCyGui directory
   - Run `.\build_windows_local.ps1`

3. The script will automatically:
   - Install Chocolatey (if not present)
   - Install CMake
   - Install Visual Studio Build Tools
   - Install Windows SDK
   - Build SDL3 and FreeType from source
   - Build the Python wheel

## Build Output

### Local Development Build

After a successful build:
- Wheel file: `dist/dearcygui-*.whl`
- Built SDL3 library: `build_SDL/Release/SDL3-static.lib`
- Built FreeType library: `build_FT/Release/freetype.lib`

To install the built wheel:
```batch
pip install dist\dearcygui-*.whl
```

Or if you used the `-Install` flag, the package is already installed in development mode.

### Multi-Version Build

After a successful build:
- Wheel files: `wheelhouse/dearcygui-*-win_amd64.whl` (one for each Python version)

## Troubleshooting

### "Python is not installed or not in PATH"

Make sure Python is installed and added to your PATH:
1. Reinstall Python with "Add Python to PATH" checked
2. Or manually add Python to PATH in System Environment Variables

### "Access Denied" or permission errors

Run PowerShell as Administrator:
1. Search for "PowerShell" in Start menu
2. Right-click and select "Run as Administrator"

### Build fails with "cmake not found"

If the automatic installation fails:
1. Manually install CMake from: https://cmake.org/download/
2. Add CMake to PATH
3. Re-run the build script with `-SkipDependencies`

### Build fails with "MSVC not found" or compiler errors

If the automatic installation fails:
1. Manually install Visual Studio Build Tools from: https://visualstudio.microsoft.com/downloads/
2. During installation, select "Desktop development with C++"
3. Re-run the build script with `-SkipDependencies`

### Git submodules not initialized

If you get errors about missing files in `thirdparty/`:
```batch
git submodule update --init --recursive
```

### Build is very slow

This is normal for the first build. Subsequent builds will be faster because:
- SDL3 and FreeType are already built (unless you clean)
- Cython-generated C++ files are cached

To speed up rebuilds:
- Don't use `-Clean` flag unless necessary
- Only rebuild when you modify source files

### Out of disk space

The build process needs ~4 GB of free space. Clear space by:
- Removing old build artifacts: `.\build_windows_local.ps1 -Clean`
- Deleting `build_SDL/`, `build_FT/`, `dist/`, `wheelhouse/` directories

## Advanced Usage

### Building with specific compiler flags

Edit `setup.py` and modify the `compile_args` and `linking_args` variables in the Windows section (around line 261).

### Building only for specific Python version with cibuildwheel

```powershell
# Example: Build only for Python 3.12
.\build_windows_wheels_cibuildwheel.ps1 -PythonVersions "cp312-win_amd64"
```

### Using an existing virtual environment

```batch
# Activate your virtual environment first
venv\Scripts\activate

# Then build
.\build_windows_local.ps1
```

### Development workflow

For rapid development iterations:

1. First build (with dependencies):
   ```powershell
   .\build_windows_local.ps1 -Install
   ```

2. Make your code changes

3. Rebuild (skip dependencies):
   ```powershell
   .\build_windows_local.ps1 -Install -SkipDependencies
   ```

4. Test your changes directly (package is installed in development mode)

## Differences from CI Build

The CI build (`.github/workflows/build.yml`) and local builds have a few differences:

| Aspect | CI Build | Local Build |
|--------|----------|-------------|
| Environment | GitHub Actions (Windows Server 2025) | Your local Windows PC |
| Build tool | cibuildwheel | cibuildwheel or direct build |
| Python versions | Multiple (3.10-3.14) | Single (your current Python) or multiple with cibuildwheel |
| Output location | `C:\build\wheelhouse` | `dist/` or `wheelhouse/` |
| Temp directory | `C:\temp` | `C:\temp` |

Both approaches produce compatible wheels that work on Windows 64-bit systems.

## CI Build Compatibility

The `build_windows_wheels_cibuildwheel.ps1` script is designed to match the CI build process as closely as possible. It uses the same:
- Build tool (cibuildwheel)
- Python versions
- Environment variables
- Build configuration

This ensures wheels built locally are identical to those built in CI.

## Support

If you encounter issues not covered in this guide:

1. Check the error messages carefully
2. Ensure all prerequisites are installed
3. Try running with `-Clean` flag
4. Open an issue on GitHub with:
   - Your Windows version
   - Python version (`python --version`)
   - Complete error message
   - Build command you used

## Additional Resources

- [Main README](README.md)
- [Python Packaging Guide](https://packaging.python.org/)
- [cibuildwheel documentation](https://cibuildwheel.readthedocs.io/)
- [CMake documentation](https://cmake.org/documentation/)
