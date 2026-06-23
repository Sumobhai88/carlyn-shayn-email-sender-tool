"""
Recipient Pydantic schemas
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class RecipientBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None


class RecipientCreate(RecipientBase):
    campaign_id: int


class RecipientBulkCreate(BaseModel):
    campaign_id: int
    recipients: List[RecipientBase]


class RecipientResponse(RecipientBase):
    id: int
    campaign_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class RecipientUploadResponse(BaseModel):
    success: bool
    total_contacts: int
    valid_contacts: int
    invalid_contacts: int
    duplicate_contacts: int
    errors: List[str] = []
