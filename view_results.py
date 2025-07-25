#!/usr/bin/env python3
"""
Simple script to start the web viewer for documentation review results.
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

def main():
    print("🌐 Documentation Review Web Viewer")
    print("="*50)
    
    # Check for JSON files
    json_files = list(Path('.').glob('documentation_review_*.json'))
    json_files.extend(list(Path('.').glob('review_results.json')))
    
    if not json_files:
        print("❌ No review files found!")
        print("Please run the documentation reviewer first:")
        print("  python run_review.py")
        print("  or")
        print("  python docs_reviewer.py")
        return
    
    print(f"📂 Found {len(json_files)} review files to display")
    for f in json_files:
        print(f"  • {f.name}")
    
    print("\n🚀 Starting web server...")
    print("📡 Server will start at: http://localhost:5002")
    print("🌐 Your browser should open automatically")
    print("⏹️  Press Ctrl+C to stop the server")
    print("="*50)
    
    # Import and start the Flask app
    try:
        from app import app
        
        # Wait a moment then open browser
        def open_browser():
            time.sleep(1.5)
            webbrowser.open('http://localhost:5002')
        
        import threading
        timer = threading.Timer(1.5, open_browser)
        timer.start()
        
        # Start the web server
        app.run(debug=False, host='0.0.0.0', port=5002)
        
    except ImportError:
        print("❌ Flask not installed. Please install dependencies:")
        print("  pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error starting web server: {e}")

if __name__ == "__main__":
    main() 