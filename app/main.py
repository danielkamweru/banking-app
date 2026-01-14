from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy.orm import Session
from app import crud,schemas,database
from .database import engine, BASE
from . import models

models.BASE.metadata.create_all(bind=engine)

app= FastAPI()

@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session=Depends(database.get_db)):
    
    return crud.create_user_with_account(db=db, user=user)