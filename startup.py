#!/usr/bin/env python3
"""
Startup script for the banking application
Handles database schema setup before starting the server
"""
import os
import sys
import time
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
        # Import and run the schema fix
        from fix_schema import fix_database_schema
        print("Setting up database schema...")
        fix_database_schema()
        print("Database schema setup completed!")
        return True
    except Exception as e:
        print(f"Error setting up database: {e}")
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
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Server stopped by user")
        sys.exit(0)

def main():
    """Main startup function"""
    load_dotenv()
    
    print("=== Banking App Startup ===")
    
    # Wait for database to be available
    if not wait_for_database():
        print("Database unavailable, exiting...")
        sys.exit(1)
    
    # Setup database schema
    if not setup_database():
        print("Database setup failed, exiting...")
        sys.exit(1)
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()
