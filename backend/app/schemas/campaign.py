"""
Campaign Pydantic schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.campaign import CampaignStatus


class CampaignBase(BaseModel):
    campaign_name: str = Field(..., min_length=1, max_length=200)
    subject: str = Field(..., min_length=1, max_length=500)
    template: str = Field(..., min_length=1)


class CampaignCreate(CampaignBase):
    model_config = ConfigDict(populate_by_name=True)


class CampaignUpdate(BaseModel):
    campaign_name: Optional[str] = None
    subject: Optional[str] = None
    template: Optional[str] = None
    status: Optional[CampaignStatus] = None
    
    model_config = ConfigDict(populate_by_name=True)


class CampaignResponse(BaseModel):
    id: int
    campaign_name: str
    subject: str
    template: str
    status: CampaignStatus
    total_emails: int
    sent_count: int
    delivered_count: int
    opened_count: int
    bounced_count: int
    failed_count: int
    unsubscribed_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CampaignStats(BaseModel):
    total_campaigns: int
    active_campaigns: int
    total_sent: int
    total_delivered: int
    average_open_rate: float
    average_click_rate: float
