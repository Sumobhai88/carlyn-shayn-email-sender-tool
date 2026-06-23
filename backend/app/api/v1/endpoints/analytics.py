"""
Analytics endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.db.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/overview")
async def get_analytics_overview(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    campaign_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get analytics overview"""
    service = AnalyticsService(db)
    return await service.get_overview(start_date, end_date, campaign_id)


@router.get("/email-logs")
async def get_email_logs(
    skip: int = 0,
    limit: int = Query(default=10, le=10000),  # Increased limit to 10000
    campaign_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get email logs with filters"""
    service = AnalyticsService(db)
    return await service.get_email_logs(
        skip=skip,
        limit=limit,
        campaign_id=campaign_id,
        status_filter=status_filter,
        search=search
    )


@router.get("/stats")
async def get_analytics_stats(
    campaign_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get detailed statistics"""
    service = AnalyticsService(db)
    return await service.get_stats(campaign_id)
