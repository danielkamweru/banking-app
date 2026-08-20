import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from app.database_config import database_diagnostic, get_database_url

#loading files from .env file only in local development
if os.getenv("RENDER") is None:
    load_dotenv()

DATABASE_URL = get_database_url()
print(f"Database configuration: {database_diagnostic(DATABASE_URL)}")

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "connect_timeout": 15,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
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
