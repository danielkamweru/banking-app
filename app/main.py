import os
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import engine, BASE, get_db
from app.models import User, Account
from app import crud, schemas, security
from app.mailer import send_transaction_email, send_welcome_email
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError as JoseJWTError
import alembic.config
import os

#SECURITY & CONFIG
SECRET_KEY = os.getenv("SECRET_KEY", "BANK_PROJECT_2024_SECRET_KEY_FOR_PRODUCTION")
ALGORITHM = "HS256"

#  Full TEAM
ADMIN_CC_LIST = os.getenv("ADMIN_CC_LIST", "Ashley.mararo@student.moringaschool.com,david.kuron@student.moringaschool.com,yvonne.kadenyi@student.moringaschool.com,daniel.kamweru@student.moringaschool.com,thomas.mbula@student.moringaschool.com").split(",")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

app = FastAPI(title="Money Transfer API")

# Auto-run migrations and schema fix on startup
@app.on_event("startup")
async def startup_event():
    try:
        # Run Alembic migrations first
        alembic_cfg = alembic.config.Config("alembic.ini")
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        # Add SSL settings for Render's PostgreSQL
        if DATABASE_URL and '?' not in DATABASE_URL:
            DATABASE_URL = DATABASE_URL + "?sslmode=require"
        elif DATABASE_URL and 'sslmode' not in DATABASE_URL:
            DATABASE_URL = DATABASE_URL + "&sslmode=require"
        
        alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
        from alembic import command
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations completed successfully")
        
        # Run schema fix to ensure all columns exist
        from sqlalchemy import create_engine, text
        
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"connect_timeout": 10, "sslmode": "require"}
        )
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                # Check and add missing columns
                columns_result = conn.execute(text("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'users' AND table_schema = 'public'
                """))
                existing_columns = {row[0] for row in columns_result}
                print(f"📋 Existing columns: {sorted(existing_columns)}")
                
                # Handle problematic columns if they exist
                problematic_columns = ['username', 'hashed_password']
                for col in problematic_columns:
                    if col in existing_columns:
                        print(f"🔧 Fixing {col} column constraint...")
                        try:
                            conn.execute(text(f"ALTER TABLE users ALTER COLUMN {col} DROP NOT NULL"))
                            print(f"✅ Removed NOT NULL constraint from {col} column")
                        except Exception as e:
                            print(f"⚠️ Could not fix {col} constraint: {e}")
                
                required_columns = ['first_name', 'last_name', 'email', 'hashed_pin', 'created_at']
                
                for col in required_columns:
                    if col not in existing_columns:
                        print(f"➕ Adding missing column: {col}")
                        if col in ['first_name', 'last_name']:
                            conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} VARCHAR DEFAULT 'Unknown'"))
                            conn.execute(text(f"UPDATE users SET {col} = 'Unknown' WHERE {col} IS NULL"))
                            conn.execute(text(f"ALTER TABLE users ALTER COLUMN {col} SET NOT NULL"))
                        elif col == 'created_at':
                            conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
                        elif col == 'hashed_pin':
                            conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} VARCHAR DEFAULT 'temp_hash'"))
                            conn.execute(text(f"UPDATE users SET {col} = 'temp_hash' WHERE {col} IS NULL"))
                            conn.execute(text(f"ALTER TABLE users ALTER COLUMN {col} SET NOT NULL"))
                        else:
                            conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} VARCHAR DEFAULT ''"))
                            conn.execute(text(f"UPDATE users SET {col} = '' WHERE {col} IS NULL"))
                            conn.execute(text(f"ALTER TABLE users ALTER COLUMN {col} SET NOT NULL"))
                
                trans.commit()
                print("✅ Schema verification completed")
            except Exception as e:
                trans.rollback()
                print(f"⚠️ Schema fix warning: {e}")
                
    except Exception as e:
        print(f"❌ Migration error: {e}")

if __name__ == "__main__":
    import uvicorn
    import socket
    port = 8000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", port)) == 0:
            import subprocess, sys
            subprocess.run(["fuser", "-k", f"{port}/tcp"])
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)

@app.api_route("/", methods=["GET", "HEAD"])
def read_root():
    return {"message": "Banking App API is live!"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AUTHENTICATION DEPENDENCY
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JoseJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# AUTH ROUTES

@app.post("/api/auth/signup", response_model=schemas.UserResponse)
async def signup(user: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        new_user = crud.create_user_with_account(db=db, user=user)
        account = db.query(Account).filter(Account.user_id == new_user.id).first()
        background_tasks.add_task(
            send_welcome_email,
            email=new_user.email,
            name=f"{new_user.first_name} {new_user.last_name}",
            account_number=account.account_number if account else "N/A"
        )
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user or not security.verify_pin(user_credentials.pin, user.hashed_pin):
        raise HTTPException(status_code=401, detail="Invalid email or PIN")

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# USER MANAGEMENT ROUTES

@app.get("/api/users/me", response_model=schemas.UserResponse)
def get_current_user_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/api/users/me", response_model=schemas.UserResponse)
def update_profile(
    update_data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update first name, last name, or email"""
    return crud.update_user_profile(db, current_user.id, update_data)

@app.patch("/api/users/me/reset-pin")
def reset_pin(
    pin_data: schemas.PinReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reset the user's PIN"""
    success = crud.update_user_pin(db, current_user.id, pin_data.new_pin)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "PIN updated successfully. Use your new PIN for the next login."}

@app.delete("/api/users/me")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete the current user and their account"""
    success = crud.delete_user_and_account(db, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Account successfully deleted."}

# BANKING ROUTES

@app.post("/api/transactions/deposit")
async def deposit(
    deposit_data: schemas.DepositCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if deposit_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive")

    account = crud.deposit_funds(db, current_user.id, deposit_data.amount)

    background_tasks.add_task(
        send_transaction_email,
        email=current_user.email,
        name=current_user.first_name,
        amount=deposit_data.amount,
        balance=account.initial_balance,
        type="Deposit",
        cc_emails=ADMIN_CC_LIST
    )

    return {
        "message": f"Deposit successful. Confirmation email sent.",
        "new_balance": account.initial_balance,
        "account_number": account.account_number
    }

@app.post("/api/transactions/transfer")
async def transfer(
    transfer_data: schemas.TransferCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sender_account = db.query(Account).filter(Account.user_id == current_user.id).first()
    if not sender_account:
        raise HTTPException(status_code=404, detail="Sender account not found")

    result = crud.transfer_money(
        db=db,
        sender_account_id=sender_account.id,
        receiver_acc_number=transfer_data.receiver_acc_number,
        amount=transfer_data.amount
    )

    background_tasks.add_task(
        send_transaction_email,
        email=current_user.email,
        name=current_user.first_name,
        amount=transfer_data.amount,
        balance=result["new_balance"],
        type="Transfer",
        cc_emails=ADMIN_CC_LIST
    )

    return result

@app.get("/api/transactions", response_model=list[schemas.TransactionBase])
def read_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.get_user_transactions(db, user_id=current_user.id)

@app.get("/reset-db")
def reset_db():
    from app.database import BASE, engine
    BASE.metadata.drop_all(bind=engine)
    BASE.metadata.create_all(bind=engine)
    return {"message": "Database reset successfully"}

@app.get("/force-reset")
def force_reset(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == "premiumresearch5@gmail.com").first()
    if user:
        user.hashed_pin = security.hash_pin("8888")
        db.commit()
        return {"message": "PIN forced back to 8888"}
    return {"error": "User not found"}
