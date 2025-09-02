@echo off
echo Opening Trading Portfolio in Chrome...
echo.

REM Try to open Chrome with localhost:5000
set CHROME_FOUND=0

REM Try Chrome in Program Files
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "http://localhost:5000"
    set CHROME_FOUND=1
    goto :found
)

REM Try Chrome in Program Files (x86)
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" "http://localhost:5000"
    set CHROME_FOUND=1
    goto :found
)

REM Try Chrome in user's AppData
if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    start "" "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" "http://localhost:5000"
    set CHROME_FOUND=1
    goto :found
)

REM If Chrome not found, try using the default browser
if %CHROME_FOUND%==0 (
    echo Chrome not found, opening with default browser...
    start "" "http://localhost:5000"
    goto :found
)

:found
echo Chrome opened successfully!
echo.
echo If the Flask app is not running, start it first with:
echo python flask_app.py
echo.
pause
