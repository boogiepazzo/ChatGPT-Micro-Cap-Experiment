#!/usr/bin/env python3
"""
Startup script for the Flask Trading Portfolio Application
"""

import os
import sys
from pathlib import Path

def main():
    """Start the Flask application with proper setup"""
    
    # Change to the correct directory
    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)
    
    # Add parent directory to path for imports
    parent_dir = script_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    print("Starting Flask Trading Portfolio Application...")
    print(f"Working directory: {script_dir}")
    print(f"Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Import and run the Flask app
        from flask_app import app
        
        with app.app_context():
            # Create database tables if they don't exist
            from flask_app import db
            db.create_all()
            print("Database initialized successfully")
        
        # Run the application
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"Error importing Flask app: {e}")
        print("Make sure you have installed the requirements:")
        print("pip install -r requirements_flask.txt")
        return 1
    except Exception as e:
        print(f"Error starting Flask app: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
