from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

# Password hashing configuration
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# SECURITY CONSTANTS
SECRET_KEY = "BANK_PROJECT_2024_SECRET" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_pin(pin: str) -> str:
    """Hashes the PIN for secure storage."""
    return pwd_context.hash(pin[:72])

def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    """Verifies a plain PIN against the stored hash."""
    return pwd_context.verify(plain_pin, hashed_pin)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Creates a JWT access token. 
    Standardizes the 'sub' as a string for consistency.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Encodes the data using the secret key
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict | None:
    """
    Decodes a JWT token. Returns the payload dict if successful, 
    otherwise returns None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # If the key is wrong or token is expired, it comes here
        return None