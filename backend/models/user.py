from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# OTP Models
class SendOTPRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    phone: Optional[str] = None
    created_at: datetime
    
class UserInDB(BaseModel):
    id: str
    email: EmailStr
    name: str
    phone: Optional[str] = None
    hashed_password: str
    created_at: datetime

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    phone: Optional[str] = None
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
