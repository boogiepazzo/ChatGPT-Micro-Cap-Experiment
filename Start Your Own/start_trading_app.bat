@echo off
echo ========================================
echo   Trading Portfolio Web Application
echo ========================================
echo.

REM Change to the correct directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing Flask dependencies...
    pip install -r requirements_flask.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if Chrome is available
reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Chrome not found in registry
    echo Will try to find Chrome in common locations...
)

REM Start Flask app in background
echo Starting Flask application...
start /B python flask_app.py

REM Wait a moment for Flask to start
echo Waiting for Flask to start...
timeout /t 3 /nobreak >nul

REM Try to open Chrome with localhost:5000
echo Opening Chrome to http://localhost:5000...

REM Try multiple Chrome locations
set CHROME_FOUND=0

REM Try Chrome in Program Files
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "http://localhost:5000"
    set CHROME_FOUND=1
)

REM Try Chrome in Program Files (x86)
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" "http://localhost:5000"
    set CHROME_FOUND=1
)

REM Try Chrome in user's AppData
if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    start "" "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" "http://localhost:5000"
    set CHROME_FOUND=1
)

REM If Chrome not found, try using the default browser
if %CHROME_FOUND%==0 (
    echo Chrome not found, opening with default browser...
    start "" "http://localhost:5000"
)

echo.
echo ========================================
echo   Application Started Successfully!
echo ========================================
echo.
echo Flask app is running at: http://localhost:5000
echo Chrome should have opened automatically
echo.
echo To stop the application:
echo 1. Close this window
echo 2. Or press Ctrl+C in the Flask console
echo.
echo Press any key to close this window...
pause >nul
