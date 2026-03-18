@echo off
setlocal enabledelayedexpansion

:: -----------------------------------------
:: Visual Studio Code Installer Script
:: -----------------------------------------

set "VSCODE_URL=https://update.code.visualstudio.com/latest/win32-x64-user/stable"
set "INSTALLER=VSCodeSetup.exe"
set "LOGFILE=vscode_install.log"

echo ============================================
echo   Visual Studio Code Install/Uninstall Tool
echo ============================================
echo.

echo Choose an option:
echo   1. Install VS Code
echo   2. Uninstall VS Code
echo   3. Exit
echo.

set /p choice="Enter choice (1/2/3): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto uninstall
if "%choice%"=="3" exit /b

echo Invalid choice.
exit /b

:: -----------------------------------------
:: INSTALL VS CODE
:: -----------------------------------------
:install
echo Downloading VS Code installer...
powershell -Command "(New-Object Net.WebClient).DownloadFile('%VSCODE_URL%', '%INSTALLER%')" >> "%LOGFILE%" 2>&1

if not exist "%INSTALLER%" (
    echo Failed to download installer.
    exit /b
)

echo Running installer...
"%INSTALLER%" /VERYSILENT /MERGETASKS=!runcode,addcontextmenufiles,addcontextmenufolders,associatewithfiles,addtopath >> "%LOGFILE%" 2>&1

echo Installation complete.
del "%INSTALLER%"
exit /b

:: -----------------------------------------
:: UNINSTALL VS CODE
:: -----------------------------------------
:uninstall
echo Searching for VS Code uninstall entry...

for /f "tokens=2*" %%A in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall" /s /f "Visual Studio Code" ^| findstr "UninstallString"') do (
    set "UNINSTALL_CMD=%%B"
)

for /f "tokens=2*" %%A in ('reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall" /s /f "Visual Studio Code" ^| findstr "UninstallString"') do (
    set "UNINSTALL_CMD=%%B"
)

if not defined UNINSTALL_CMD (
    echo VS Code is not installed.
    exit /b
)

echo Uninstalling VS Code...
"%UNINSTALL_CMD%" /VERYSILENT >> "%LOGFILE%" 2>&1

echo Uninstall complete.
exit /b
