"""
User schemas for API requests/responses
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None


class UserCreate(UserBase):
    google_id: str


class UserUpdate(UserBase):
    pass


class UserInDB(UserBase):
    id: int
    google_id: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: datetime
    email_limit: Optional[int] = 1000
    emails_used: Optional[int] = 0
    is_blocked: Optional[bool] = False
    
    class Config:
        from_attributes = True


class User(UserInDB):
    pass


class GoogleLoginRequest(BaseModel):
    token: str


class GoogleLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
