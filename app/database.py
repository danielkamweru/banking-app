import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

#loading files from .env file only in local development
if os.getenv("RENDER") is None:
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is missing!")

# Fix for Render.com postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Add SSL settings for Render's PostgreSQL
if '?' not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL + "?sslmode=require"
elif 'sslmode' not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL + "&sslmode=require"

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"connect_timeout": 10, "sslmode": "require"}
)


#CREATING SESSIONLOCAL

SessionLocal= sessionmaker(autocommit=False,autoflush=False,bind=engine)

#CREATING BASE
BASE= declarative_base()

#CREATING DATABASE DEPENDANCY

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()