import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

#loading files from .env file

load_dotenv()
DATABASE_URL=os.getenv('DATABASE_URL')

#creating an engine
engine = create_engine(DATABASE_URL)


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