#!/usr/bin/env python3
"""
Manual migration runner for when auto-migrations fail.
Usage: python run_migrations.py
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
if os.getenv("RENDER") is None:
    load_dotenv()

def run_migrations():
    """Run Alembic migrations with retry logic"""
    import alembic.config
    from sqlalchemy import create_engine, text
    
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"\n🚀 Running migrations (Attempt {retry_count + 1}/{max_retries})")
            
            DATABASE_URL = os.getenv("DATABASE_URL")
            if not DATABASE_URL:
                print("❌ DATABASE_URL environment variable not set!")
                sys.exit(1)
            
            # Fix postgres:// to postgresql://
            if DATABASE_URL.startswith('postgres://'):
                DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
                print("✅ Fixed postgres:// -> postgresql://")
            
            # Add SSL settings
            if '?' not in DATABASE_URL:
                DATABASE_URL = DATABASE_URL + "?sslmode=prefer"
            elif 'sslmode' not in DATABASE_URL:
                DATABASE_URL = DATABASE_URL + "&sslmode=prefer"
            
            # Test connection first
            print("🔗 Testing database connection...")
            test_engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                connect_args={
                    "connect_timeout": 20,
                    "keepalives": 1,
                    "keepalives_idle": 30,
                }
            )
            
            with test_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("✅ Database connection validated!")
            
            # Run migrations
            print("\n📦 Running Alembic migrations...")
            alembic_cfg = alembic.config.Config("alembic.ini")
            alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
            
            from alembic import command
            command.upgrade(alembic_cfg, "head")
            
            print("✅ Migrations completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            retry_count += 1
            
            if retry_count < max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff
                print(f"⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"\n❌ Failed after {max_retries} attempts")
                return False
    
    return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
