"""
SMTP Profile Pydantic schemas with comprehensive validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


class SMTPProfileBase(BaseModel):
    """Base schema with common fields"""
    profile_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique name for the SMTP profile",
        example="Gmail SMTP"
    )
    sender_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Display name for sent emails",
        example="Carlyn Shayn Email Engine"
    )
    sender_email: EmailStr = Field(
        ...,
        description="Valid email address for From field",
        example="noreply@carlyshayn.com"
    )
    smtp_host: str = Field(
        ...,
        min_length=1,
        description="SMTP server hostname",
        example="smtp.gmail.com"
    )
    smtp_port: int = Field(
        ...,
        ge=1,
        le=65535,
        description="SMTP port number (1-65535)",
        example=587
    )
    username: str = Field(
        ...,
        min_length=1,
        description="SMTP authentication username",
        example="noreply@carlyshayn.com"
    )
    tls_enabled: bool = Field(
        default=True,
        description="Enable TLS/SSL encryption",
        example=True
    )

    @field_validator('smtp_host')
    @classmethod
    def validate_smtp_host(cls, v):
        """Validate SMTP host format"""
        if not v or len(v.strip()) == 0:
            raise ValueError('SMTP host cannot be empty')
        # Basic validation - could be enhanced
        if ' ' in v:
            raise ValueError('SMTP host cannot contain spaces')
        return v.strip()
    
    @field_validator('profile_name')
    @classmethod
    def validate_profile_name(cls, v):
        """Validate profile name"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Profile name cannot be empty')
        return v.strip()


class SMTPProfileCreate(SMTPProfileBase):
    """Schema for creating new SMTP profile"""
    password: str = Field(
        ...,
        min_length=1,
        description="SMTP authentication password (will be encrypted)",
        example="your_secure_password"
    )

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Password cannot be empty')
        if len(v) < 4:
            raise ValueError('Password must be at least 4 characters')
        return v


class SMTPProfileUpdate(BaseModel):
    """Schema for updating SMTP profile - all fields optional"""
    profile_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        example="Updated Gmail SMTP"
    )
    sender_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        example="Updated Sender Name"
    )
    sender_email: Optional[EmailStr] = Field(
        None,
        example="updated@carlyshayn.com"
    )
    smtp_host: Optional[str] = Field(
        None,
        min_length=1,
        example="smtp.gmail.com"
    )
    smtp_port: Optional[int] = Field(
        None,
        ge=1,
        le=65535,
        example=587
    )
    username: Optional[str] = Field(
        None,
        min_length=1,
        example="updated@carlyshayn.com"
    )
    password: Optional[str] = Field(
        None,
        min_length=1,
        description="New password (will be encrypted)",
        example="new_secure_password"
    )
    tls_enabled: Optional[bool] = Field(
        None,
        example=True
    )
    is_active: Optional[bool] = Field(
        None,
        description="Set as active profile",
        example=False
    )

    @field_validator('profile_name', 'sender_name', 'smtp_host', 'username', 'password')
    @classmethod
    def validate_optional_text(cls, v):
        """Reject whitespace-only updates while preserving omitted fields."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError('Field cannot be empty')
        if ' ' in v and v.strip() == v and v.count(' ') == len(v):
            raise ValueError('Field cannot be empty')
        return v.strip()


class SMTPProfileResponse(SMTPProfileBase):
    """Schema for SMTP profile response (password hidden)"""
    id: int = Field(..., description="Profile ID", example=1)
    is_active: bool = Field(..., description="Is currently active", example=True)
    status: str = Field(
        ...,
        description="Connection status",
        example="connected"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "profile_name": "Gmail SMTP",
                "sender_name": "Carlyn Shayn",
                "sender_email": "noreply@carlyshayn.com",
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "noreply@carlyshayn.com",
                "tls_enabled": True,
                "is_active": True,
                "status": "connected",
                "created_at": "2024-06-17T10:30:00Z",
                "updated_at": "2024-06-17T11:15:00Z"
            }
        }


class SMTPTestRequest(BaseModel):
    """Schema for SMTP connection test request"""
    profile_id: int = Field(
        ...,
        description="SMTP profile ID to test",
        example=1
    )
    test_email: Optional[EmailStr] = Field(
        None,
        description="Optional email address to send test email",
        example="test@example.com"
    )


class SMTPTestResponse(BaseModel):
    """Schema for SMTP connection test response"""
    success: bool = Field(
        ...,
        description="Whether connection test was successful",
        example=True
    )
    message: str = Field(
        ...,
        description="Test result message",
        example="Connection successful and test email sent"
    )
    status: str = Field(
        ...,
        description="Updated connection status",
        example="connected"
    )
    profile_id: Optional[int] = Field(
        None,
        description="Profile ID that was tested",
        example=1
    )
    test_email: Optional[str] = Field(
        None,
        description="Email address test was sent to",
        example="test@example.com"
    )
    error_details: Optional[str] = Field(
        None,
        description="Error details if test failed",
        example=None
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Connection successful and test email sent",
                "status": "connected",
                "profile_id": 1,
                "test_email": "test@example.com",
                "error_details": None
            }
        }


class SMTPConnectionStatus(BaseModel):
    """Schema for profile connection status summary"""
    id: int = Field(..., description="Profile ID")
    profile_name: str = Field(..., description="Profile name")
    status: str = Field(..., description="Connection status")
    is_active: bool = Field(..., description="Is active profile")
    last_tested: Optional[datetime] = Field(None, description="Last test timestamp")

    class Config:
        from_attributes = True
