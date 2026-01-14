from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import engine, BASE, get_db

from app.models import User, Account, Transaction 
from app import crud, schemas

print("--- DATABASE SYNC STARTING ---")
try:
    BASE.metadata.create_all(bind=engine)
    print("--- DATABASE TABLES CREATED/VERIFIED SUCCESSFULLY ---")
except Exception as e:
    print(f"--- ERROR CREATING TABLES: {e} ---")

app = FastAPI(title="Money Transfer API")



@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Creates a new user and an associated bank account automatically.
    """
    return crud.create_user_with_account(db=db, user=user)


@app.post("/deposit/{account_id}")
def deposit(account_id: int, amount: float, db: Session = Depends(get_db)):
    """
    Adds funds to a specific account and records the transaction.
    """
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive")
        
    account = crud.deposit_funds(db, account_id, amount)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    return {
        "message": "Deposit successful", 
        "account_number": account.account_number,
        "new_balance": account.initial_balance
    }
    
    


@app.post("/transfer")
def transfer(sender_id: int, receiver_number: str, amount: float, db: Session = Depends(get_db)):
    """
    Transfers money from the sender's account to a receiver's account number.
    """
    # In a real app, sender_id would be extracted from a secure JWT token
    return crud.transfer_money(db, sender_id, receiver_number, amount)

#route to check history of transaction
@app.get("/transactions/{user_id}", response_model=list[schemas.TransactionBase])
def read_transactions(user_id: int, db: Session = Depends(get_db)):
    transactions = crud.get_user_transactions(db, user_id=user_id)
    return transactions

