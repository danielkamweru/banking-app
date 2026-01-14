from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy.orm import Session
from app import crud,schemas,database



app= FastAPI()

@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session=Depends(database.get_db)):
    
    return crud.create_user_with_account(db=db, user=user)