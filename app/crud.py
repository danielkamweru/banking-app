from sqlalchemy.orm import Session
from app import models, schemas, security
import uuid



#creating a user
def create_user_with_account(db:Session, user: schemas.UserCreate):
    #ENSURING THE PIN IS HASHED BEFORE SAVING
    hashed_pin=security.hash_pin(user.pin)
    
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
    
    #creating the user account
    new_account = models.Account(
        user_id= db_user.id,
        initial_balance= 0.00,
        account_number = "GROUP8-" + str(db_user.id).zfill(4)
     
    )
    db.add(new_account)
    db.commit()
    
    
    return db_user

#creating an account linked to the user
