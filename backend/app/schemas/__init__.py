"""
Pydantic schemas package
"""
from app.schemas.smtp_profile import (
    SMTPProfileCreate,
    SMTPProfileUpdate,
    SMTPProfileResponse,
    SMTPTestRequest,
    SMTPTestResponse,
    SMTPConnectionStatus
)

from app.schemas.progress import (
    CampaignProgressResponse,
    BulkProgressResponse,
    ProgressUpdateRequest
)

__all__ = [
    "SMTPProfileCreate",
    "SMTPProfileUpdate",
    "SMTPProfileResponse",
    "SMTPTestRequest",
    "SMTPTestResponse",
    "SMTPConnectionStatus",
    "CampaignProgressResponse",
    "BulkProgressResponse",
    "ProgressUpdateRequest"
]
