# Windows Build Quick Start

Quick reference for building DearCyGui on Windows.

## Prerequisites

1. Install Python 3.10+ from https://www.python.org/downloads/
2. Install Git from https://git-scm.com/download/win
3. Clone repo: `git clone --recursive https://github.com/valmcc/DearCyGui.git`

## Quick Build Commands

### For Development (Single Python Version)

```powershell
# PowerShell (run as Administrator first time)
.\build_windows_local.ps1

# Or using Command Prompt
build_windows_local.bat
```

Output: `dist/dearcygui-*.whl`

### For Distribution (Multiple Python Versions)

```powershell
# PowerShell (run as Administrator first time)
.\build_windows_wheels_cibuildwheel.ps1
```

Output: `wheelhouse/dearcygui-*-win_amd64.whl`

## Common Options

### Local Build
- `.\build_windows_local.ps1 -Clean` - Clean previous build
- `.\build_windows_local.ps1 -Install` - Build and install
- `.\build_windows_local.ps1 -SkipDependencies` - Skip installing system dependencies

### Multi-Version Build
- `.\build_windows_wheels_cibuildwheel.ps1 -SkipDependencies` - Skip installing system dependencies
- `.\build_windows_wheels_cibuildwheel.ps1 -OutputDir "C:\wheels"` - Custom output directory

## Installation

```batch
pip install dist\dearcygui-*.whl
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python not found" | Add Python to PATH |
| "Access denied" | Run PowerShell as Administrator |
| "cmake not found" | Install CMake manually or re-run script |
| "Missing files in thirdparty/" | Run `git submodule update --init --recursive` |
| Build is slow | Normal for first build; subsequent builds faster |

## What Gets Installed Automatically

First build installs (requires Administrator):
- Chocolatey package manager
- CMake
- Visual Studio Build Tools
- Windows SDK 10.0

Subsequent builds with `-SkipDependencies` skip these.

## Full Documentation

See [BUILDING_WINDOWS.md](BUILDING_WINDOWS.md) for complete guide.
