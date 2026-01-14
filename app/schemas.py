from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: int
    pin: str 

class UserResponse(BaseModel):
    id: int
    first_name: str
    email: str
    
    
    class Config:
        from_attributes = True