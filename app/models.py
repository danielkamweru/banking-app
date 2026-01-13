from sqlalchemy import Column, Integer, String,Float,DateTime,ForeignKey
from app.database import BASE
from datetime import datetime,timezone
from sqlalchemy.orm import relationship

class User(BASE):
    __tablename__ = "users"
    
    id = Column(Integer,primary_key=True,index=True)
    first_name = Column(String,nullable= False)
    last_name = Column(String,nullable= False)
    email = Column(String,nullable=False)
    phone_number= Column(Integer,nullable=False)
    hashed_pin = Column(Integer,nullable= False)
    created_at = Column(DateTime, default= lambda: datetime.now(timezone.utc))
    
    #LINKING THE USER TO THEIR ACCOUNT
    account = relationship("Account", back_populates="owner", uselist=False)
    
    


class Account(BASE):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, index=True)
    initial_balance = Column(Float, default=0.00)
    user_id = Column(Integer,ForeignKey("users.id"))
    
    #Relationships
    owner = relationship("User", back_populates="account")
    transactions = relationship("Transaction", back_populates="account")
    
    
class Transaction(BASE):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    reference_code = Column(String, unique=True, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String)
    timestamp = Column(DateTime,default= lambda: datetime.now(timezone.utc))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    account = relationship("Account", back_populates="transactions")