from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import engine, BASE, get_db
from app.models import User, Account, Transaction 
from app import crud, schemas, security
from fastapi.security import OAuth2PasswordBearer

# This defines where the token is sent from the frontend
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

print("--- DATABASE SYNC STARTING ---")
try:
    BASE.metadata.create_all(bind=engine)
    print("--- DATABASE TABLES CREATED/VERIFIED SUCCESSFULLY ---")
except Exception as e:
    print(f"--- ERROR CREATING TABLES: {e} ---")

app = FastAPI(title="Money Transfer API")

#AUTH DEPENDENCY 
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = security.decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

#AUTH ROUTES

@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user_with_account(db=db, user=user)

@app.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()

    if not user or not security.verify_pin(user_credentials.pin, user.hashed_pin):
        raise HTTPException(status_code=401, detail="Invalid email or PIN")

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

#BANKING ROUTES 

@app.post("/deposit")
def deposit(amount: float, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Adds funds to the logged-in user's account.
    """
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive")
    
    # Use the account ID from the logged-in user
    account = crud.deposit_funds(db, current_user.id, amount)
    return {"message": "Deposit successful", "new_balance": account.initial_balance}

@app.post("/transfer")
def transfer(receiver_number: str, amount: float, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Securely transfers money from the current user to a recipient.
    """
    # Now sender_id is pulled automatically from the JWT (current_user.id)
    return crud.transfer_money(db, current_user.id, receiver_number, amount)

@app.get("/my-transactions", response_model=list[schemas.TransactionBase])
def read_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Only shows transactions belonging to the logged-in user.
    """
    return crud.get_user_transactions(db, user_id=current_user.id)