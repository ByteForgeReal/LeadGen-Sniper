@echo off
echo =======================================================
echo     ByteForge - LeadGen Sniper Professional Release
echo =======================================================
echo.
echo This script will automate the creation of a GitHub Release (v1.0.0)
echo and upload your standalone executable (LeadGen-Sniper.exe).
echo.
echo Requirements: You must have a GitHub Personal Access Token (classic)
echo with the 'repo' scope.
echo.
echo Press any key to start the release process...
pause >nul

echo.
echo Installing requirements...
pip install requests -q
if %errorlevel% neq 0 (
    echo [Error] Failed to install 'requests' library. Please check your Python installation.
    pause
    exit /b
)

echo.
python github_release.py

echo.
echo =======================================================
echo                     Process Complete
echo =======================================================
pause
