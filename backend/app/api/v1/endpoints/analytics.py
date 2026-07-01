"""
Analytics endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/overview")
async def get_analytics_overview(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    campaign_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = AnalyticsService(db)
    return await service.get_overview(start_date, end_date, campaign_id)


@router.get("/email-logs")
async def get_email_logs(
    skip: int = 0,
    limit: int = Query(default=10, le=10000),
    campaign_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = AnalyticsService(db)
    return await service.get_email_logs(
        skip=skip, limit=limit,
        campaign_id=campaign_id,
        status_filter=status_filter,
        search=search,
        user_id=current_user.id
    )


@router.get("/stats")
async def get_analytics_stats(
    campaign_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = AnalyticsService(db)
    return await service.get_stats(campaign_id, user_id=current_user.id)
