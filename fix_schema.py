#!/usr/bin/env python3
"""
Direct schema fix for production database
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from app.database import BASE, DATABASE_URL, database_diagnostic

load_dotenv()

print(f"Database configuration: {database_diagnostic(DATABASE_URL)}")

def fix_database_schema():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            print("🔍 Checking current schema...")
            
            # Check if users table exists
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'users'
            """))
            
            if not result.fetchone():
                print("❌ Users table doesn't exist - creating it...")
                # Create users table with correct schema
                conn.execute(text("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        first_name VARCHAR NOT NULL,
                        last_name VARCHAR NOT NULL,
                        email VARCHAR NOT NULL UNIQUE,
                        hashed_pin VARCHAR NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("✅ Users table created")
            else:
                print("📋 Users table exists - checking columns...")
                
                # Check for missing columns
                columns_result = conn.execute(text("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'users' AND table_schema = 'public'
                """))
                existing_columns = {row[0] for row in columns_result}
                
                required_columns = ['first_name', 'last_name', 'email', 'hashed_pin', 'created_at']
                
                for col in required_columns:
                    if col not in existing_columns:
                        print(f"➕ Adding missing column: {col}")
                        if col in ['first_name', 'last_name']:
                            conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} VARCHAR NOT NULL DEFAULT ''"))
                        elif col == 'created_at':
                            conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
                        else:
                            conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} VARCHAR NOT NULL"))
                
                # Fix any NULL values in first_name/last_name
                conn.execute(text("""
                    UPDATE users SET first_name = 'Unknown' WHERE first_name IS NULL OR first_name = ''
                """))
                conn.execute(text("""
                    UPDATE users SET last_name = 'Unknown' WHERE last_name IS NULL OR last_name = ''
                """))
            
            # Check and create accounts table
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'accounts'
            """))
            
            if not result.fetchone():
                print("➕ Creating accounts table...")
                conn.execute(text("""
                    CREATE TABLE accounts (
                        id SERIAL PRIMARY KEY,
                        account_number VARCHAR UNIQUE NOT NULL,
                        initial_balance FLOAT DEFAULT 0.0,
                        user_id INTEGER REFERENCES users(id)
                    )
                """))
                print("✅ Accounts table created")
            
            # Check and create transactions table
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'transactions'
            """))
            
            if not result.fetchone():
                print("➕ Creating transactions table...")
                conn.execute(text("""
                    CREATE TABLE transactions (
                        id SERIAL PRIMARY KEY,
                        reference_code VARCHAR UNIQUE NOT NULL,
                        amount FLOAT NOT NULL,
                        transaction_type VARCHAR NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        sender_id INTEGER REFERENCES accounts(id),
                        receiver_id INTEGER REFERENCES accounts(id)
                    )
                """))
                print("✅ Transactions table created")
            
            # Create indexes
            print("📊 Creating indexes...")
            try:
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users(email)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_id ON users(id)"))
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_accounts_account_number ON accounts(account_number)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_accounts_id ON accounts(id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_transactions_id ON transactions(id)"))
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_transactions_reference_code ON transactions(reference_code)"))
                print("✅ Indexes created")
            except Exception as e:
                print(f"⚠️  Index creation warning: {e}")
            
            # Commit transaction
            trans.commit()
            print("🎉 Database schema fixed successfully!")
            
            # Verify the fix
            print("🔍 Verifying schema...")
            test_result = conn.execute(text("SELECT first_name, last_name, email FROM users LIMIT 1"))
            print("✅ Schema verification passed!")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error fixing schema: {e}")
            raise

if __name__ == "__main__":
    fix_database_schema()
