from passlib.context import CryptContext
pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")



SECRET_KEY = "your-super-secret-key-here" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_pin(pin:str):
    return pwd_context.hash(pin)

def verify_pin(plain_pin:str,hashed_pin:str):
    return pwd_context.verify(plain_pin,hashed_pin)