from sqlalchemy.orm import Session
from app import models, schemas, security
import uuid
from fastapi import HTTPException, status



#creating a user
def create_user_with_account(db:Session, user: schemas.UserCreate):
    #ENSURING THE PIN IS HASHED BEFORE SAVING
    hashed_pin=security.hash_pin(user.pin)
    
    db_user= models.User(
      first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
       # phone_number=getattr(user, 'phone_number', None),
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
    
    db.refresh(db_user)
    
    
    return db_user

#DEPOSITING MONEY

def deposit_funds(db: Session, account_id: int, amount: float):
    #Finding the account
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        return None

    #Update balance
    account.initial_balance += amount

    #Create History Record
    new_transaction = models.Transaction(
        reference_code=f"DEP-{uuid.uuid4().hex[:8].upper()}",
        amount=amount,
        transaction_type="DEPOSIT",
        receiver_id=account.id,
        sender_id=None 
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(account)
    return account

#transfering money
def transfer_money(db: Session, sender_account_id: int, receiver_acc_number: str, amount: float):
  #quering both accounts
    sender_acc = db.query(models.Account).filter(models.Account.id == sender_account_id).first()
    receiver_acc = db.query(models.Account).filter(models.Account.account_number == receiver_acc_number).first()

  #making validations
    if not receiver_acc:
        raise HTTPException(status_code=404, detail="Recipient account not found")
    
    if sender_acc.id == receiver_acc.id:
        raise HTTPException(status_code=400, detail="You cannot send money to yourself")

    if sender_acc.initial_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

   #math logic
    sender_acc.initial_balance -= amount
    receiver_acc.initial_balance += amount

    #  Creating the Transaction Record
    new_tx = models.Transaction(
        reference_code=f"TRF-{uuid.uuid4().hex[:8].upper()}",
        amount=amount,
        transaction_type="TRANSFER",
        sender_id=sender_acc.id,
        receiver_id=receiver_acc.id
    )

    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    
    return {
        "reference_code": new_tx.reference_code,
        "message": "Confirmed that Transfer was Successful",
        
        "new_balance": sender_acc.initial_balance,
        "receiver_name": f"{receiver_acc.owner.first_name} {receiver_acc.owner.last_name}"
    }
    
    #function to get transaction history
    
def get_user_transactions(db: Session, user_id: int):
    return db.query(models.Transaction).filter(
        (models.Transaction.sender_id == user_id) | 
        (models.Transaction.receiver_id == user_id)
    ).all()