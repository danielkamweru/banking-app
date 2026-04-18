#!/usr/bin/env python3
"""
Startup script for the banking application
Handles database schema setup before starting the server
"""
import os
import sys
import time
import traceback
from dotenv import load_dotenv

def wait_for_database():
    """Wait for database to be available"""
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import OperationalError
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is missing!")
    
    # Fix for Render.com postgres:// to postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    max_retries = 10
    retry_interval = 5
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database is available!")
            return True
        except OperationalError as e:
            print(f"Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                print("Failed to connect to database after maximum retries")
                return False

def setup_database():
    """Setup database schema"""
    try:
        print("Importing fix_schema module...")
        from fix_schema import fix_database_schema
        print("Setting up database schema...")
        fix_database_schema()
        print("Database schema setup completed!")
        return True
    except ImportError as e:
        print(f"Import error in fix_schema: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"Error setting up database: {e}")
        traceback.print_exc()
        return False

def start_server():
    """Start the FastAPI server"""
    import subprocess
    
    print("Starting FastAPI server...")
    # Use gunicorn with PORT from environment (Render provides this)
    port = os.getenv("PORT", "8000")
    cmd = [
        "gunicorn", 
        "-k", "uvicorn.workers.UvicornWorker", 
        "app.main:app", 
        "--bind", f"0.0.0.0:{port}"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    try:
        print("Executing gunicorn command...")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to start server: {e}")
        traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        print("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error starting server: {e}")
        traceback.print_exc()
        sys.exit(1)

def main():
    """Main startup function"""
    try:
        print("Using Render environment variables...")
        
        print("=== Banking App Startup ===")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        print(f"Environment variables loaded: PORT={os.getenv('PORT')}, DATABASE_URL={'SET' if os.getenv('DATABASE_URL') else 'NOT SET'}")
        
        # Wait for database to be available
        print("Step 1: Waiting for database...")
        if not wait_for_database():
            print("Database unavailable, exiting...")
            sys.exit(1)
        
        # Setup database schema
        print("Step 2: Setting up database schema...")
        if not setup_database():
            print("Database setup failed, exiting...")
            sys.exit(1)
        
        # Start the server
        print("Step 3: Starting server...")
        start_server()
        
    except Exception as e:
        print(f"Fatal error in main startup: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
