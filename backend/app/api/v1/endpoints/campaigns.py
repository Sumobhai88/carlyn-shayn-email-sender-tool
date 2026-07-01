"""
Campaign endpoints — all routes require authentication, all data is user-scoped
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignStats
from app.schemas.recipient import RecipientUploadResponse
from app.schemas.progress import BulkProgressResponse
from app.services.campaign_service import CampaignService
from app.services.campaign_engine import campaign_engine

router = APIRouter()


# ── Collection ────────────────────────────────────────────────────────────────

@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await CampaignService(db).create_campaign(campaign, user_id=current_user.id)


@router.get("/")
async def get_campaigns(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaigns = await CampaignService(db).get_campaigns(skip=skip, limit=limit, user_id=current_user.id)
    return {"campaigns": campaigns}


@router.get("/stats", response_model=CampaignStats)
async def get_campaign_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await CampaignService(db).get_stats(user_id=current_user.id)


@router.post("/fix-stats")
async def fix_campaign_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.campaign import Campaign
    from app.models.email_log import EmailLog
    try:
        campaigns = db.query(Campaign).filter(Campaign.user_id == current_user.id).all()
        for c in campaigns:
            q = db.query(EmailLog).filter(EmailLog.campaign_id == c.id)
            c.sent_count = q.count()
            c.delivered_count = q.filter(EmailLog.delivery_status == "delivered").count()
            c.failed_count = q.filter(EmailLog.delivery_status == "failed").count()
            c.opened_count = q.filter(EmailLog.opened == True).count()
            c.bounced_count = q.filter(EmailLog.bounced == True).count()
            c.unsubscribed_count = q.filter(EmailLog.unsubscribed == True).count()
        db.commit()
        return {"success": True, "message": f"Fixed statistics for {len(campaigns)} campaigns", "campaigns_fixed": len(campaigns)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress/all", response_model=BulkProgressResponse)
async def get_all_campaigns_progress(
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return campaign_engine.get_all_progress(db)


# ── Per-campaign ──────────────────────────────────────────────────────────────

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    c = await CampaignService(db).get_campaign(campaign_id, user_id=current_user.id)
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return c


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int, campaign_update: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await CampaignService(db).update_campaign(campaign_id, campaign_update, user_id=current_user.id)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await CampaignService(db).delete_campaign(campaign_id, user_id=current_user.id)
    return None


@router.post("/{campaign_id}/upload-recipients", response_model=RecipientUploadResponse)
async def upload_recipients(
    campaign_id: int, file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await CampaignService(db).upload_recipients(campaign_id, file)


@router.post("/{campaign_id}/start")
async def start_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await CampaignService(db).start_campaign(campaign_id)


@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await CampaignService(db).pause_campaign(campaign_id)


@router.post("/{campaign_id}/resume")
async def resume_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await CampaignService(db).resume_campaign(campaign_id)


@router.post("/{campaign_id}/stop")
async def stop_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await CampaignService(db).stop_campaign(campaign_id)


@router.get("/{campaign_id}/progress")
async def get_campaign_progress(
    campaign_id: int, response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return await CampaignService(db).get_campaign_progress(campaign_id)
