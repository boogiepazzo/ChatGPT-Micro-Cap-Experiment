@echo off
echo Creating Desktop Shortcut for Trading Portfolio App...
echo.

REM Get the current directory
set "CURRENT_DIR=%~dp0"
set "BATCH_FILE=%CURRENT_DIR%start_trading_app.bat"

REM Get desktop path
for /f "tokens=2*" %%a in ('reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop 2^>nul') do set "DESKTOP=%%b"

REM Create the shortcut
echo Creating shortcut on desktop...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Trading Portfolio.lnk'); $Shortcut.TargetPath = '%BATCH_FILE%'; $Shortcut.WorkingDirectory = '%CURRENT_DIR%'; $Shortcut.Description = 'Launch Trading Portfolio Web Application'; $Shortcut.IconLocation = '%CURRENT_DIR%flask_app.py,0'; $Shortcut.Save()"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   Shortcut Created Successfully!
    echo ========================================
    echo.
    echo A shortcut named "Trading Portfolio" has been created on your desktop.
    echo Double-click it to start the application.
    echo.
    echo The shortcut will:
    echo - Start the Flask web server
    echo - Open Chrome to http://localhost:5000
    echo - Install dependencies if needed
    echo.
) else (
    echo.
    echo ERROR: Failed to create shortcut
    echo You can still run the app by double-clicking:
    echo %BATCH_FILE%
    echo.
)

pause
