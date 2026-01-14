from sqlalchemy import Column, Integer, String,Float,DateTime,ForeignKey,BigInteger
from app.database import BASE
from datetime import datetime,timezone
from sqlalchemy.orm import relationship

class User(BASE):
    __tablename__ = "users"
    
    id = Column(Integer,primary_key=True,index=True)
    first_name = Column(String,nullable= False)
    last_name = Column(String,nullable= False)
    email = Column(String,nullable=False)
    hashed_pin = Column(String,nullable= False)
    created_at = Column(DateTime, default= lambda: datetime.now(timezone.utc))
    
    #LINKING THE USER TO THEIR ACCOUNT

    
    account = relationship("Account", back_populates="owner", uselist=False)
    
    


class Account(BASE):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, index=True)
    initial_balance = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    #relationships
    
    owner = relationship("User", back_populates="account")
    sent_transactions = relationship("Transaction", foreign_keys="[Transaction.sender_id]", back_populates="sender_account")
    received_transactions = relationship("Transaction", foreign_keys="[Transaction.receiver_id]", back_populates="receiver_account")

class Transaction(BASE):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    reference_code = Column(String, unique=True, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String) 
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
   
    sender_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    receiver_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

  # Relationships 
    sender_account = relationship("Account", foreign_keys=[sender_id], back_populates="sent_transactions")
    receiver_account = relationship("Account", foreign_keys=[receiver_id], back_populates="received_transactions")