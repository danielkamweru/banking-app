from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Define what the Account data should look like
class AccountResponse(BaseModel):
    account_number: str
    initial_balance: float

    class Config:
        from_attributes = True

# Define the User response (including the account)
class UserResponse(BaseModel):
    id: int
    first_name: str
    email: str
    account: Optional[AccountResponse] = None 
    
    class Config:
        from_attributes = True


#userlogin
class UserLogin(BaseModel):
    email: EmailStr
    pin: str

# Define the Transaction record (The "Statement" line)
class TransactionBase(BaseModel):
    id: int
    sender_id: Optional[int] = None    # Optional prevents 500 errors if ID is null
    receiver_id: Optional[int] = None  
    amount: float
    timestamp: datetime

    class Config:
        from_attributes = True

# For creating a new user
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    pin: str