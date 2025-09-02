# Trading Portfolio App Launchers

This folder contains several launcher scripts to make it easy to start the Trading Portfolio web application.

## Available Launchers

### 1. `start_trading_app.bat` (Recommended)
**What it does:**
- Checks if Python is installed
- Installs Flask dependencies if needed
- Starts the Flask web server
- Automatically opens Chrome to http://localhost:5000
- Handles multiple Chrome installation locations

**How to use:**
- Double-click the file
- Wait for the setup to complete
- Chrome will open automatically to the trading app

### 2. `start_trading_app.ps1` (PowerShell Version)
**What it does:**
- Same functionality as the .bat file
- Uses PowerShell for better error handling
- More reliable on modern Windows systems

**How to use:**
- Right-click the file and select "Run with PowerShell"
- Or open PowerShell and run: `.\start_trading_app.ps1`

### 3. `open_trading_app.bat` (Simple Browser Opener)
**What it does:**
- Only opens Chrome to http://localhost:5000
- Does NOT start the Flask server
- Use this if the Flask app is already running

**How to use:**
- Double-click to open the app in Chrome
- Make sure Flask is running first with: `python flask_app.py`

### 4. `create_desktop_shortcut.bat`
**What it does:**
- Creates a desktop shortcut for easy access
- The shortcut will launch the full application

**How to use:**
- Run once to create the shortcut
- Double-click the "Trading Portfolio" shortcut on your desktop

## Quick Start Guide

### First Time Setup:
1. **Create Desktop Shortcut:**
   - Double-click `create_desktop_shortcut.bat`
   - This creates a shortcut on your desktop

2. **Launch the App:**
   - Double-click the "Trading Portfolio" shortcut on your desktop
   - Or double-click `start_trading_app.bat`

### Daily Use:
- Double-click the desktop shortcut
- Wait for Chrome to open
- Start trading!

## Troubleshooting

### Chrome Not Found
If Chrome isn't automatically detected, the launcher will:
- Try common Chrome installation locations
- Fall back to your default browser
- Still work perfectly!

### Python Not Found
If you get a "Python not found" error:
1. Install Python from https://python.org
2. Make sure to check "Add Python to PATH" during installation
3. Restart your computer
4. Try the launcher again

### Dependencies Not Installed
The launcher will automatically install Flask dependencies if needed. If it fails:
1. Open Command Prompt
2. Navigate to this folder
3. Run: `pip install -r requirements_flask.txt`
4. Try the launcher again

### Port Already in Use
If you get a "port 5000 already in use" error:
1. Close any other Flask applications
2. Or change the port in `flask_app.py` (line 481)
3. Restart the launcher

## Manual Launch (Alternative)

If the launchers don't work, you can start manually:

1. **Open Command Prompt**
2. **Navigate to this folder:**
   ```cmd
   cd "C:\Users\Foncho\Documents\GitHub\ChatGPT-Micro-Cap-Experiment\Start Your Own"
   ```

3. **Install dependencies:**
   ```cmd
   pip install -r requirements_flask.txt
   ```

4. **Start Flask:**
   ```cmd
   python flask_app.py
   ```

5. **Open browser:**
   - Go to http://localhost:5000
   - Or double-click `open_trading_app.bat`

## Features

✅ **Automatic Setup:** Installs dependencies if needed  
✅ **Chrome Detection:** Finds Chrome in multiple locations  
✅ **Error Handling:** Clear error messages and solutions  
✅ **Desktop Shortcut:** One-click access from desktop  
✅ **Background Launch:** Flask runs in background  
✅ **Cross-Browser:** Falls back to default browser if Chrome not found  

## File Structure

```
Start Your Own/
├── start_trading_app.bat          # Main launcher (recommended)
├── start_trading_app.ps1          # PowerShell version
├── open_trading_app.bat           # Browser opener only
├── create_desktop_shortcut.bat    # Creates desktop shortcut
├── flask_app.py                   # Flask web application
├── requirements_flask.txt         # Python dependencies
└── LAUNCHER_README.md            # This file
```

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Try the manual launch method
3. Make sure Python and Chrome are properly installed
4. Check that no other applications are using port 5000

The launchers are designed to be user-friendly and handle most common issues automatically!
