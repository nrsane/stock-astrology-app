#!/usr/bin/env python3
"""
Script to install dependencies with compatibility fixes
"""
import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return success status"""
    try:
        print(f"🚀 Running: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("📦 Starting dependency installation...")
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip==23.0.1")
    
    # Install setuptools and wheel first
    run_command(f"{sys.executable} -m pip install setuptools==68.0.0 wheel==0.38.4")
    
    # Install requirements
    success = run_command(f"{sys.executable} -m pip install -r requirements.txt")
    
    if success:
        print("🎉 All dependencies installed successfully!")
    else:
        print("💥 Some dependencies failed to install")
        sys.exit(1)

if __name__ == "__main__":
    main()
