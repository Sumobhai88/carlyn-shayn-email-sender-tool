"""
Campaign endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignStats
)
from app.schemas.recipient import RecipientUploadResponse
from app.schemas.progress import CampaignProgressResponse, BulkProgressResponse
from app.services.campaign_service import CampaignService
from app.services.campaign_engine import campaign_engine

router = APIRouter()


# ── Collection / stats (static paths first — must come before /{id} routes) ──

@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db)
):
    """Create a new campaign"""
    service = CampaignService(db)
    return await service.create_campaign(campaign)


@router.get("/")
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all campaigns"""
    service = CampaignService(db)
    campaigns = await service.get_campaigns(skip=skip, limit=limit)
    return {"campaigns": campaigns}


@router.get("/stats", response_model=CampaignStats)
async def get_campaign_stats(db: Session = Depends(get_db)):
    """Get overall campaign statistics"""
    service = CampaignService(db)
    return await service.get_stats()


@router.post("/fix-stats")
async def fix_campaign_stats(db: Session = Depends(get_db)):
    """Fix campaign statistics by recalculating from email_logs"""
    from app.models.campaign import Campaign
    from app.models.email_log import EmailLog
    
    try:
        campaigns = db.query(Campaign).all()
        fixed_count = 0
        
        for campaign in campaigns:
            logs_query = db.query(EmailLog).filter(EmailLog.campaign_id == campaign.id)
            
            campaign.sent_count = logs_query.count()
            campaign.delivered_count = logs_query.filter(EmailLog.delivery_status == "delivered").count()
            campaign.failed_count = logs_query.filter(EmailLog.delivery_status == "failed").count()
            campaign.opened_count = logs_query.filter(EmailLog.opened == True).count()
            campaign.bounced_count = logs_query.filter(EmailLog.bounced == True).count()
            campaign.unsubscribed_count = logs_query.filter(EmailLog.unsubscribed == True).count()
            fixed_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Fixed statistics for {fixed_count} campaigns",
            "campaigns_fixed": fixed_count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fix statistics: {str(e)}"
        )


@router.get(
    "/progress/all",
    response_model=BulkProgressResponse,
    summary="Get progress for all active campaigns",
    description=(
        "Returns a real-time snapshot of every campaign that is currently "
        "running or paused. Useful for a dashboard overview widget. "
        "Cache-Control headers prevent stale responses."
    ),
)
async def get_all_campaigns_progress(
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Aggregate progress across all running / paused campaigns.

    Returns:
    - **active_count**: number of campaigns actively sending
    - **paused_count**: number of campaigns paused
    - **campaigns**: full CampaignProgress list for each active/paused campaign
    - **snapshot_at**: UTC timestamp of this snapshot
    """
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"  # disable nginx buffering

    return campaign_engine.get_all_progress(db)


# ── Per-campaign routes ───────────────────────────────────────────────────────

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get campaign by ID"""
    service = CampaignService(db)
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    db: Session = Depends(get_db)
):
    """Update campaign"""
    service = CampaignService(db)
    return await service.update_campaign(campaign_id, campaign_update)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Delete campaign"""
    service = CampaignService(db)
    await service.delete_campaign(campaign_id)
    return None


@router.post("/{campaign_id}/upload-recipients", response_model=RecipientUploadResponse)
async def upload_recipients(
    campaign_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload campaign contacts from a CSV or XLSX file"""
    service = CampaignService(db)
    return await service.upload_recipients(campaign_id, file)


# ── Campaign Execution Controls ───────────────────────────────────────────────

@router.post("/{campaign_id}/start")
async def start_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Start sending a campaign in the background.

    Launches a daemon thread that sends emails sequentially with a
    random 20–60 second delay between each send.
    The API returns immediately — sending continues in the background.
    """
    service = CampaignService(db)
    return await service.start_campaign(campaign_id)


@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Pause a running campaign.

    The current email (if mid-send) will complete, then the thread pauses.
    Use /resume to continue from where it left off.
    """
    service = CampaignService(db)
    return await service.pause_campaign(campaign_id)


@router.post("/{campaign_id}/resume")
async def resume_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Resume a paused campaign.

    The background thread continues sending from the next pending contact.
    """
    service = CampaignService(db)
    return await service.resume_campaign(campaign_id)


@router.post("/{campaign_id}/stop")
async def stop_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Stop a running or paused campaign.

    The thread exits after completing the current email.
    Campaign status is set to 'completed'.
    """
    service = CampaignService(db)
    return await service.stop_campaign(campaign_id)


# ── Progress Tracking ─────────────────────────────────────────────────────────

@router.get(
    "/{campaign_id}/progress",
    response_model=None,  # Temporarily disabled for debugging
    summary="Get live campaign progress",
    description=(
        "Returns a real-time progress snapshot for the given campaign. "
        "Safe to poll every 1–5 seconds from the frontend. "
        "Cache-Control headers prevent stale responses."
    ),
)
async def get_campaign_progress(
    campaign_id: int,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Real-time progress for a single campaign.

    Tracks:
    - **total**: total recipient count
    - **sent**: emails accepted by SMTP server
    - **delivered**: emails confirmed delivered
    - **failed**: emails that failed after retries
    - **pending**: recipients not yet attempted
    - **progress_pct**: `(sent + failed) / total × 100`
    - **elapsed_seconds**: seconds since campaign started sending
    - **estimated_remaining_seconds**: ETA based on current send rate
    - **send_rate_per_hour**: current throughput in emails/hour
    - **snapshot_at**: UTC timestamp of this response
    """
    # Prevent browser / proxy / CDN from caching progress responses
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"  # disable nginx proxy buffering

    service = CampaignService(db)
    return await service.get_campaign_progress(campaign_id)
