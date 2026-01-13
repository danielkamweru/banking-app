from sqlalchemy.orm import Session
from app import models, schemas, security
import uuid




def create_user(db:Session, user: schemas.UserCreate):
    #ENSURING THE PIN IS HASHED BEFORE SAVING
    hashed_pin=security.hash_pin(user.pin)
    
    
    #creating a user
    db_user= models.User(
      first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number=user.phone_number,
        hashed_pin=hashed_pin
    )
    
    #saving the user to postgres
    
    db.add(db_user)
    db.commit()
    
    
    db.refresh(db_user)
    
    return db_user