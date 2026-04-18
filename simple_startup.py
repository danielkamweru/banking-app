#!/usr/bin/env python3
"""
Simple startup script that just starts the server
"""
import os
import subprocess
import sys
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    print("=== Simple Banking App Startup ===")
    print(f"PORT: {os.getenv('PORT', '8000')}")
    print(f"DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT SET'}")
    
    # Start the server directly
    port = os.getenv("PORT", "8000")
    cmd = [
        "gunicorn", 
        "-k", "uvicorn.workers.UvicornWorker", 
        "app.main:app", 
        "--bind", f"0.0.0.0:{port}"
    ]
    
    print(f"Starting server with command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
