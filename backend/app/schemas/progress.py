"""
Campaign progress tracking schemas for real-time monitoring
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CampaignProgressResponse(BaseModel):
    """
    Real-time campaign progress response
    Used for frontend polling to show live sending progress
    """
    campaign_id: int = Field(..., description="Campaign ID", example=1)
    campaign_name: str = Field(..., description="Campaign name", example="Summer Sale 2024")
    status: str = Field(
        ..., 
        description="Campaign status: draft, running, paused, completed, failed",
        example="running"
    )
    
    # Email counts
    total_emails: int = Field(
        ..., 
        description="Total emails to send",
        example=1000
    )
    sent_count: int = Field(
        ..., 
        description="Emails sent (attempted)",
        example=850
    )
    delivered_count: int = Field(
        ..., 
        description="Emails successfully delivered",
        example=820
    )
    failed_count: int = Field(
        ..., 
        description="Emails failed to deliver",
        example=30
    )
    pending_count: int = Field(
        ..., 
        description="Emails pending/queued",
        example=150
    )
    
    # Additional metrics
    opened_count: int = Field(
        default=0,
        description="Emails opened",
        example=250
    )
    bounced_count: int = Field(
        default=0,
        description="Emails bounced",
        example=10
    )
    unsubscribed_count: int = Field(
        default=0,
        description="Unsubscribe count",
        example=5
    )
    
    # Progress percentage
    percentage: float = Field(
        ..., 
        description="Progress percentage (0-100)",
        example=85.0
    )
    
    # Rates
    delivery_rate: float = Field(
        default=0.0,
        description="Delivery rate percentage",
        example=96.5
    )
    open_rate: float = Field(
        default=0.0,
        description="Open rate percentage",
        example=30.5
    )
    bounce_rate: float = Field(
        default=0.0,
        description="Bounce rate percentage",
        example=1.2
    )
    
    # Timing
    started_at: Optional[datetime] = Field(
        None,
        description="Campaign start time"
    )
    estimated_completion: Optional[datetime] = Field(
        None,
        description="Estimated completion time"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="Actual completion time"
    )
    
    # Speed metrics
    emails_per_minute: float = Field(
        default=0.0,
        description="Current sending rate (emails/minute)",
        example=50.5
    )
    time_elapsed_seconds: int = Field(
        default=0,
        description="Time elapsed since start (seconds)",
        example=1020
    )
    time_remaining_seconds: int = Field(
        default=0,
        description="Estimated time remaining (seconds)",
        example=180
    )
    
    # Status indicators
    is_active: bool = Field(
        default=False,
        description="Is campaign currently sending",
        example=True
    )
    is_completed: bool = Field(
        default=False,
        description="Is campaign completed",
        example=False
    )
    has_errors: bool = Field(
        default=False,
        description="Does campaign have errors",
        example=False
    )
    
    # Last update
    last_updated: datetime = Field(
        ...,
        description="Last progress update timestamp"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "campaign_id": 1,
                "campaign_name": "Summer Sale 2024",
                "status": "running",
                "total_emails": 1000,
                "sent_count": 850,
                "delivered_count": 820,
                "failed_count": 30,
                "pending_count": 150,
                "opened_count": 250,
                "bounced_count": 10,
                "unsubscribed_count": 5,
                "percentage": 85.0,
                "delivery_rate": 96.5,
                "open_rate": 30.5,
                "bounce_rate": 1.2,
                "started_at": "2024-06-17T10:00:00Z",
                "estimated_completion": "2024-06-17T10:05:00Z",
                "completed_at": None,
                "emails_per_minute": 50.5,
                "time_elapsed_seconds": 1020,
                "time_remaining_seconds": 180,
                "is_active": True,
                "is_completed": False,
                "has_errors": False,
                "last_updated": "2024-06-17T10:17:00Z"
            }
        }


class BulkProgressResponse(BaseModel):
    """
    Progress for multiple campaigns
    Useful for dashboard overview
    """
    total_campaigns: int = Field(..., description="Total campaigns tracked")
    active_campaigns: int = Field(..., description="Currently active campaigns")
    campaigns: list[CampaignProgressResponse] = Field(
        ...,
        description="List of campaign progress data"
    )
    last_updated: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "total_campaigns": 5,
                "active_campaigns": 2,
                "campaigns": [
                    {
                        "campaign_id": 1,
                        "campaign_name": "Summer Sale 2024",
                        "status": "running",
                        "total_emails": 1000,
                        "sent_count": 850,
                        "delivered_count": 820,
                        "failed_count": 30,
                        "pending_count": 150,
                        "percentage": 85.0,
                        "is_active": True
                    }
                ],
                "last_updated": "2024-06-17T10:17:00Z"
            }
        }


class ProgressUpdateRequest(BaseModel):
    """
    Request to update campaign progress
    Used internally by email sender
    """
    campaign_id: int = Field(..., description="Campaign ID")
    sent_count: Optional[int] = Field(None, description="Update sent count")
    delivered_count: Optional[int] = Field(None, description="Update delivered count")
    failed_count: Optional[int] = Field(None, description="Update failed count")
    status: Optional[str] = Field(None, description="Update campaign status")

    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": 1,
                "sent_count": 850,
                "delivered_count": 820,
                "failed_count": 30,
                "status": "running"
            }
        }
