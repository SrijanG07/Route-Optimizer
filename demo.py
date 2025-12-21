#!/usr/bin/env python3
"""
Quick Demo Script for Route Optimizer
Starts the server and opens the UI in the browser.
"""

import subprocess
import webbrowser
import time
import sys
import os

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import fastapi
        import uvicorn
        import pydantic
        import geopy
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n🔧 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def check_env():
    """Check if .env file exists."""
    if not os.path.exists(".env"):
        print("⚠️  No .env file found")
        print("📝 Creating .env from .env.example...")
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as example, open(".env", "w") as env:
                env.write(example.read())
            print("✅ Created .env file")
            print("\n⚠️  IMPORTANT: Add your GEMINI_API_KEY to .env file")
            print("   Get your free API key at: https://makersuite.google.com/app/apikey")
            input("\nPress Enter after adding your API key...")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("✅ .env file exists")
    return True

def start_server():
    """Start the FastAPI server."""
    print("\n🚀 Starting server...")
    print("📍 Server will run at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("\n⏸️  Press Ctrl+C to stop the server\n")
    
    # Start server in subprocess
    server = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Open browser
    print("🌐 Opening browser...")
    webbrowser.open("http://localhost:8000")
    
    print("\n✅ Demo is ready!")
    print("🎯 Try optimizing a route with priorities")
    print("🔄 Test real-time recalculation features")
    
    try:
        server.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping server...")
        server.terminate()
        print("✅ Server stopped")

if __name__ == "__main__":
    print("=" * 60)
    print("🚚 ROUTE OPTIMIZER - QUICK DEMO")
    print("=" * 60)
    print()
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_env():
        sys.exit(1)
    
    start_server()
