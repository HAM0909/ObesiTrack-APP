from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

from pydantic import validator

class UserCreate(UserBase):
    password: str

    @validator('email')
    def clean_email(cls, v: str) -> str:
        return v.replace(" ", "").strip()

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None  # Fixed: Use square brackets
    username: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None