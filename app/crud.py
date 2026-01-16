from sqlalchemy.orm import Session
from app import models, schemas, security
import uuid
from fastapi import HTTPException, status

# USER & ACCOUNT CREATION

def create_user_with_account(db: Session, user: schemas.UserCreate):
    # Check if user with this email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_pin = security.hash_pin(user.pin)

    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_pin=hashed_pin
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    new_account = models.Account(
        user_id=db_user.id,
        initial_balance=0.00,
        account_number="GROUP8-" + str(db_user.id).zfill(4)
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)  # Refresh the account instead

    # Load the account relationship
    db.refresh(db_user)
    return db_user

# USER MANAGEMENT

def update_user_profile(db: Session, user_id: int, update_data: schemas.UserUpdate):
    """Updates user personal details."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    
    # Update only provided fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_pin(db: Session, user_id: int, new_pin: str):
    """Hashes and updates a user's PIN."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.hashed_pin = security.hash_pin(new_pin)
        db.commit()
        return True
    return False

def delete_user_and_account(db: Session, user_id: int):
    """Deletes a user and their associated account/transactions."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        # Delete associated account first
        db_account = db.query(models.Account).filter(models.Account.user_id == user_id).first()
        if db_account:
            db.delete(db_account)
        # Delete the user
        db.delete(db_user)
        db.commit()
        return True
    return False

#BANKING OPERATIONS 

def deposit_funds(db: Session, user_id: int, amount: float):
    account = db.query(models.Account).filter(models.Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.initial_balance += amount 

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

def transfer_money(db: Session, sender_account_id: int, receiver_acc_number: str, amount: float):
    sender_acc = db.query(models.Account).filter(models.Account.id == sender_account_id).first()
    receiver_acc = db.query(models.Account).filter(models.Account.account_number == receiver_acc_number).first()

    if not receiver_acc:
        raise HTTPException(status_code=404, detail="Recipient account not found")
    
    if sender_acc.id == receiver_acc.id:
        raise HTTPException(status_code=400, detail="You cannot send money to yourself")

    if sender_acc.initial_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    sender_acc.initial_balance -= amount
    receiver_acc.initial_balance += amount

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

def get_user_transactions(db: Session, user_id: int):
    # Find the account first to get the account ID
    account = db.query(models.Account).filter(models.Account.user_id == user_id).first()
    if not account:
        return []
        
    return db.query(models.Transaction).filter(
        (models.Transaction.sender_id == account.id) | 
        (models.Transaction.receiver_id == account.id)
    ).all()