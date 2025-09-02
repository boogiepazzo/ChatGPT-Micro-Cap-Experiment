# Trading Portfolio Web Application Launcher
# PowerShell Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Trading Portfolio Web Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to the script directory
Set-Location $PSScriptRoot

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Flask is installed
try {
    python -c "import flask" 2>$null
    Write-Host "Flask dependencies found" -ForegroundColor Green
} catch {
    Write-Host "Installing Flask dependencies..." -ForegroundColor Yellow
    pip install -r requirements_flask.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Function to find Chrome
function Find-Chrome {
    $chromePaths = @(
        "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "${env:LOCALAPPDATA}\Google\Chrome\Application\chrome.exe"
    )
    
    foreach ($path in $chromePaths) {
        if (Test-Path $path) {
            return $path
        }
    }
    return $null
}

# Find Chrome
$chromePath = Find-Chrome
if ($chromePath) {
    Write-Host "Chrome found at: $chromePath" -ForegroundColor Green
} else {
    Write-Host "Chrome not found, will use default browser" -ForegroundColor Yellow
}

# Start Flask app in background
Write-Host "Starting Flask application..." -ForegroundColor Yellow
$flaskJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot
    python flask_app.py
}

# Wait a moment for Flask to start
Write-Host "Waiting for Flask to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Open Chrome or default browser
Write-Host "Opening browser to http://localhost:5000..." -ForegroundColor Yellow

if ($chromePath) {
    Start-Process $chromePath -ArgumentList "http://localhost:5000"
} else {
    Start-Process "http://localhost:5000"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Application Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Flask app is running at: http://localhost:5000" -ForegroundColor White
Write-Host "Browser should have opened automatically" -ForegroundColor White
Write-Host ""
Write-Host "To stop the application:" -ForegroundColor Yellow
Write-Host "1. Close this window" -ForegroundColor White
Write-Host "2. Or press Ctrl+C in the Flask console" -ForegroundColor White
Write-Host ""

# Keep the window open
Read-Host "Press Enter to close this window"
