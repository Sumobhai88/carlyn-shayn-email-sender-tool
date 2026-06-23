"""
Campaign progress tracking endpoints for real-time monitoring
Frontend polls these endpoints to show live sending progress
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.progress import (
    CampaignProgressResponse,
    BulkProgressResponse,
    ProgressUpdateRequest
)
from app.services.progress_service import ProgressService
from app.core.exceptions import CampaignNotFoundError

router = APIRouter()


# ==============================================================================
# GET - Single campaign progress
# ==============================================================================

@router.get(
    "/campaigns/{campaign_id}",
    response_model=CampaignProgressResponse,
    summary="Get Campaign Progress",
    description="Get real-time progress for a specific campaign (optimized for polling)",
    response_description="Live campaign progress data"
)
async def get_campaign_progress(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Get real-time progress for a campaign
    
    Frontend should poll this endpoint every 2-5 seconds
    during active campaign sending
    
    Path Parameters:
    - campaign_id: Campaign ID to track
    
    Returns:
    - Complete progress data including:
      - Email counts (sent, delivered, failed, pending)
      - Progress percentage
      - Delivery/open/bounce rates
      - Sending speed (emails per minute)
      - Time elapsed and estimated remaining
      - Status indicators
    
    Response is optimized for real-time updates:
    - Fast queries using indexed fields
    - Cached calculations where possible
    - Minimal overhead for frequent polling
    
    Example usage:
    ```javascript
    // Frontend polling
    setInterval(async () => {
      const progress = await fetch('/api/v1/progress/campaigns/1');
      updateUI(progress);
    }, 3000); // Poll every 3 seconds
    ```
    """
    service = ProgressService(db)
    
    try:
        progress = await service.get_campaign_progress(campaign_id)
        return progress
    except CampaignNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign progress: {str(e)}"
        )


# ==============================================================================
# GET - Multiple campaigns progress (Dashboard)
# ==============================================================================

@router.get(
    "/campaigns",
    response_model=BulkProgressResponse,
    summary="Get All Campaigns Progress",
    description="Get progress for multiple campaigns (dashboard overview)",
    response_description="Bulk progress data"
)
async def get_all_campaigns_progress(
    active_only: bool = Query(
        False,
        description="Only return active/running campaigns"
    ),
    limit: int = Query(
        50,
        ge=1,
        le=100,
        description="Maximum number of campaigns to return"
    ),
    db: Session = Depends(get_db)
):
    """
    Get progress for multiple campaigns
    
    Query Parameters:
    - active_only: Filter to only active campaigns (running, paused)
    - limit: Maximum number of campaigns (1-100)
    
    Returns:
    - List of campaign progress data
    - Total and active campaign counts
    - Last update timestamp
    
    Use cases:
    - Dashboard overview showing all active campaigns
    - Campaign list with live status
    - System monitoring
    
    Example:
    ```
    GET /api/v1/progress/campaigns?active_only=true&limit=10
    ```
    """
    service = ProgressService(db)
    
    try:
        progress = await service.get_all_progress(
            active_only=active_only,
            limit=limit
        )
        return progress
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaigns progress: {str(e)}"
        )


# ==============================================================================
# POST - Update campaign progress (Internal use)
# ==============================================================================

@router.post(
    "/campaigns/{campaign_id}/update",
    status_code=status.HTTP_200_OK,
    summary="Update Campaign Progress",
    description="Update campaign progress (used internally by email sender)",
    response_description="Success message"
)
async def update_campaign_progress(
    campaign_id: int,
    update_data: ProgressUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update campaign progress
    
    This endpoint is called internally by the email sender
    to update progress during campaign execution
    
    Path Parameters:
    - campaign_id: Campaign ID
    
    Request Body:
    - sent_count: Updated sent count
    - delivered_count: Updated delivered count
    - failed_count: Updated failed count
    - status: Updated campaign status
    
    Returns:
    - Success message
    
    Note: This is typically called by backend services,
    not directly by frontend
    """
    service = ProgressService(db)
    
    try:
        await service.update_progress(
            campaign_id=campaign_id,
            sent_count=update_data.sent_count,
            delivered_count=update_data.delivered_count,
            failed_count=update_data.failed_count,
            status=update_data.status
        )
        
        return {
            "success": True,
            "message": f"Progress updated for campaign {campaign_id}",
            "campaign_id": campaign_id
        }
    except CampaignNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update progress: {str(e)}"
        )


# ==============================================================================
# GET - Live statistics (accurate but slower)
# ==============================================================================

@router.get(
    "/campaigns/{campaign_id}/live-stats",
    summary="Get Live Statistics",
    description="Get live statistics from email logs (accurate but slower)",
    response_description="Live statistics"
)
async def get_live_statistics(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Get live statistics directly from email logs
    
    This endpoint queries the email_log table directly
    for the most accurate counts, but is slower than
    the main progress endpoint which uses cached values
    
    Use sparingly - prefer the main progress endpoint
    for frequent polling
    
    Path Parameters:
    - campaign_id: Campaign ID
    
    Returns:
    - Live counts from database:
      - sent
      - delivered
      - failed
      - pending
      - bounced
      - opened
    
    Note: Use this only when you need 100% accurate
    counts (e.g., final report after campaign completes)
    """
    service = ProgressService(db)
    
    try:
        stats = await service.get_live_stats(campaign_id)
        return {
            "campaign_id": campaign_id,
            "live_stats": stats,
            "note": "These are live counts from email logs - most accurate but slower"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get live statistics: {str(e)}"
        )


# ==============================================================================
# GET - Health check for progress tracking
# ==============================================================================

@router.get(
    "/health",
    summary="Progress API Health Check",
    description="Check if progress tracking API is operational",
    response_description="Health status"
)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check for progress tracking API
    
    Returns:
    - Status of progress tracking system
    - Database connectivity
    - API version
    """
    try:
        # Quick database check
        from app.models.campaign import Campaign
        campaign_count = db.query(Campaign).count()
        
        return {
            "status": "healthy",
            "service": "Progress Tracking API",
            "database": "connected",
            "total_campaigns": campaign_count,
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )
