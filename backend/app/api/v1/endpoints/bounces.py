"""
Bounce handling endpoints for email delivery failure management
Provides analytics and reporting for bounced emails
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.db.database import get_db
from app.services.bounce_service import BounceService

router = APIRouter()
logger = logging.getLogger(__name__)


# ==============================================================================
# BOUNCE STATISTICS
# ==============================================================================

@router.get(
    "/stats/campaign/{campaign_id}",
    summary="Get Campaign Bounce Statistics",
    description="Get comprehensive bounce statistics for a specific campaign",
    response_description="Bounce statistics"
)
async def get_campaign_bounce_stats(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Get bounce statistics for a campaign
    
    Path Parameters:
    - campaign_id: Campaign ID
    
    Returns:
    - total_sent: Total emails sent
    - total_bounced: Total bounced emails
    - successfully_delivered: Successfully delivered
    - bounce_rate: Bounce rate percentage
    - hard_bounces: Hard bounce count
    - soft_bounces: Soft bounce count
    - complaints: Spam complaint count
    - recent_bounces: List of recent bounces
    
    Example Response:
    ```json
    {
      "campaign_id": 1,
      "total_sent": 1000,
      "total_bounced": 50,
      "successfully_delivered": 950,
      "bounce_rate": 5.0,
      "hard_bounces": 30,
      "soft_bounces": 15,
      "complaints": 5,
      "recent_bounces": [...]
    }
    ```
    """
    service = BounceService(db)
    
    try:
        stats = await service.get_bounce_statistics(campaign_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting bounce statistics: {str(e)}")
        return {
            "error": "Failed to get bounce statistics",
            "details": str(e)
        }


@router.get(
    "/stats/global",
    summary="Get Global Bounce Statistics",
    description="Get bounce statistics across all campaigns",
    response_description="Global bounce statistics"
)
async def get_global_bounce_stats(db: Session = Depends(get_db)):
    """
    Get global bounce summary
    
    Returns:
    - total_emails: Total emails sent
    - total_bounced: Total bounced
    - global_bounce_rate: Overall bounce rate
    - hard/soft/complaint counts
    - unique_hard_bounced_emails: Unique emails with hard bounces
    
    Example Response:
    ```json
    {
      "total_emails": 10000,
      "total_bounced": 450,
      "global_bounce_rate": 4.5,
      "hard_bounces": 280,
      "soft_bounces": 150,
      "complaints": 20,
      "unique_hard_bounced_emails": 250
    }
    ```
    """
    service = BounceService(db)
    
    try:
        summary = await service.get_bounce_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting global bounce stats: {str(e)}")
        return {
            "error": "Failed to get global statistics",
            "details": str(e)
        }


# ==============================================================================
# BOUNCE REASONS & ANALYSIS
# ==============================================================================

@router.get(
    "/reasons/campaign/{campaign_id}",
    summary="Get Bounce Reasons",
    description="Get most common bounce reasons for a campaign",
    response_description="List of bounce reasons"
)
async def get_bounce_reasons(
    campaign_id: int,
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Get most common bounce reasons
    
    Path Parameters:
    - campaign_id: Campaign ID
    
    Query Parameters:
    - limit: Maximum number of reasons (1-100)
    
    Returns:
    - List of bounce reasons grouped by error message
    - Each entry includes bounce_type, error_message, and count
    
    Example Response:
    ```json
    [
      {
        "bounce_type": "hard",
        "error_message": "550 5.1.1 User unknown",
        "count": 25
      },
      {
        "bounce_type": "soft",
        "error_message": "Mailbox full",
        "count": 15
      }
    ]
    ```
    """
    service = BounceService(db)
    
    try:
        reasons = await service.get_bounce_reasons(campaign_id, limit)
        return {
            "campaign_id": campaign_id,
            "total_reasons": len(reasons),
            "reasons": reasons
        }
    except Exception as e:
        logger.error(f"Error getting bounce reasons: {str(e)}")
        return {
            "error": "Failed to get bounce reasons",
            "details": str(e)
        }


# ==============================================================================
# BOUNCED EMAILS LIST
# ==============================================================================

@router.get(
    "/emails",
    summary="Get Bounced Emails",
    description="Get list of bounced emails with optional filters",
    response_description="List of bounced emails"
)
async def get_bounced_emails(
    campaign_id: Optional[int] = Query(None, description="Filter by campaign ID"),
    bounce_type: Optional[str] = Query(None, description="Filter by bounce type (hard/soft/complaint)"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Get list of bounced emails
    
    Query Parameters:
    - campaign_id: Optional campaign filter
    - bounce_type: Optional bounce type filter ('hard', 'soft', 'complaint')
    - limit: Maximum number of results (1-500)
    
    Returns:
    - List of bounced emails with details
    
    Example Response:
    ```json
    {
      "total": 45,
      "filters": {
        "campaign_id": 1,
        "bounce_type": "hard"
      },
      "emails": [
        {
          "email_log_id": 123,
          "recipient_email": "user@example.com",
          "bounce_type": "hard",
          "error_message": "550 User unknown",
          "bounced_at": "2024-06-17T10:30:00Z"
        }
      ]
    }
    ```
    """
    service = BounceService(db)
    
    try:
        emails = await service.get_bounced_emails(
            campaign_id=campaign_id,
            bounce_type=bounce_type,
            limit=limit
        )
        
        return {
            "total": len(emails),
            "filters": {
                "campaign_id": campaign_id,
                "bounce_type": bounce_type
            },
            "emails": emails
        }
    except Exception as e:
        logger.error(f"Error getting bounced emails: {str(e)}")
        return {
            "error": "Failed to get bounced emails",
            "details": str(e)
        }


# ==============================================================================
# HARD BOUNCED SUPPRESSION LIST
# ==============================================================================

@router.get(
    "/suppression-list",
    summary="Get Hard Bounce Suppression List",
    description="Get list of email addresses with hard bounces (should not be emailed)",
    response_description="List of suppressed emails"
)
async def get_suppression_list(db: Session = Depends(get_db)):
    """
    Get hard bounce suppression list
    
    Returns list of email addresses that have hard bounced
    and should be excluded from future campaigns
    
    Returns:
    - List of email addresses with hard bounces
    - Count of suppressed emails
    
    Example Response:
    ```json
    {
      "total_suppressed": 150,
      "emails": [
        "bounced1@example.com",
        "bounced2@example.com"
      ],
      "note": "These emails should not be included in future campaigns"
    }
    ```
    """
    service = BounceService(db)
    
    try:
        hard_bounced = service.get_hard_bounced_emails()
        
        return {
            "total_suppressed": len(hard_bounced),
            "emails": hard_bounced,
            "note": "These emails should not be included in future campaigns"
        }
    except Exception as e:
        logger.error(f"Error getting suppression list: {str(e)}")
        return {
            "error": "Failed to get suppression list",
            "details": str(e)
        }


# ==============================================================================
# BOUNCE CHECK
# ==============================================================================

@router.get(
    "/check-email",
    summary="Check if Email is Bounced",
    description="Check if specific email address has bounced",
    response_description="Bounce status"
)
async def check_email_bounce_status(
    email: str = Query(..., description="Email address to check"),
    db: Session = Depends(get_db)
):
    """
    Check if email address has bounced
    
    Query Parameters:
    - email: Email address to check
    
    Returns:
    - is_bounced: Boolean
    - bounce_type: Type of bounce if bounced
    - should_suppress: Whether to exclude from campaigns
    
    Example Response:
    ```json
    {
      "email": "user@example.com",
      "is_bounced": true,
      "bounce_type": "hard",
      "should_suppress": true,
      "message": "This email has hard bounced and should not be emailed"
    }
    ```
    """
    service = BounceService(db)
    
    try:
        is_bounced, bounce_type = service.is_email_bounced(email)
        
        return {
            "email": email,
            "is_bounced": is_bounced,
            "bounce_type": bounce_type,
            "should_suppress": bounce_type == 'hard' if is_bounced else False,
            "message": (
                f"This email has {bounce_type} bounced and should " + 
                ("not be emailed" if bounce_type == 'hard' else "be retried later")
            ) if is_bounced else "Email has not bounced"
        }
    except Exception as e:
        logger.error(f"Error checking email bounce status: {str(e)}")
        return {
            "error": "Failed to check email status",
            "details": str(e)
        }


# ==============================================================================
# BOUNCE RECORDING (Internal Use)
# ==============================================================================

@router.post(
    "/record",
    summary="Record Bounce (Internal)",
    description="Record email bounce - used internally by email sender",
    include_in_schema=True
)
async def record_bounce(
    email_log_id: int = Query(..., description="EmailLog ID"),
    error_message: str = Query(..., description="Error message from SMTP"),
    smtp_code: Optional[str] = Query(None, description="SMTP status code"),
    db: Session = Depends(get_db)
):
    """
    Record email bounce
    
    This endpoint is called internally by the email sender
    when an SMTP failure occurs
    
    Query Parameters:
    - email_log_id: EmailLog ID
    - error_message: SMTP error message
    - smtp_code: Optional SMTP status code
    
    Returns:
    - Bounce details including type and timestamp
    """
    service = BounceService(db)
    
    try:
        result = await service.record_bounce(email_log_id, error_message, smtp_code)
        return result
    except Exception as e:
        logger.error(f"Error recording bounce: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ==============================================================================
# HEALTH CHECK
# ==============================================================================

@router.get(
    "/health",
    summary="Bounce API Health Check",
    description="Check if bounce handling API is operational"
)
async def bounce_health_check(db: Session = Depends(get_db)):
    """
    Health check for bounce handling API
    
    Returns:
    - Status of bounce handling system
    - Total bounced emails
    - Global bounce rate
    """
    try:
        from app.models.email_log import EmailLog
        
        # Quick stats
        total_bounced = db.query(EmailLog).filter(
            EmailLog.bounced == True
        ).count()
        
        total_emails = db.query(EmailLog).filter(
            EmailLog.delivery_status.in_(['sent', 'delivered', 'bounced'])
        ).count()
        
        bounce_rate = (total_bounced / total_emails * 100) if total_emails > 0 else 0.0
        
        return {
            "status": "healthy",
            "service": "Bounce Handling API",
            "database": "connected",
            "total_bounced": total_bounced,
            "total_emails": total_emails,
            "bounce_rate": round(bounce_rate, 2),
            "bounce_detection_enabled": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Bounce Handling API",
            "error": str(e)
        }
