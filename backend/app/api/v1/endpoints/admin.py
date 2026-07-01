"""
Admin endpoints - manage all users, set limits, block service
Requires is_superuser = True
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.core.dependencies import get_admin_user
from app.models.user import User
from app.models.campaign import Campaign
from app.models.email_log import EmailLog

router = APIRouter()


class SetLimitRequest(BaseModel):
    email_limit: int


class BlockRequest(BaseModel):
    is_blocked: bool


def _user_to_dict(u: User, campaign_count: int = 0, sent_count: int = 0) -> dict:
    return {
        "id": u.id,
        "name": u.name or "",
        "email": u.email,
        "picture": u.picture,
        "company_name": u.company_name or "",
        "is_active": u.is_active,
        "is_superuser": u.is_superuser,
        "is_blocked": u.is_blocked if u.is_blocked is not None else False,
        "email_limit": u.email_limit if u.email_limit is not None else 1000,
        "emails_used": u.emails_used if u.emails_used is not None else 0,
        "campaign_count": campaign_count,
        "total_sent": sent_count,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "last_login": u.last_login.isoformat() if u.last_login else None,
    }


@router.get("/users")
async def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """List all users with their usage stats"""
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    result = []
    for u in users:
        campaign_count = db.query(func.count(Campaign.id)).filter(Campaign.user_id == u.id).scalar() or 0
        sent_count = (
            db.query(func.sum(Campaign.sent_count))
            .filter(Campaign.user_id == u.id)
            .scalar() or 0
        )
        result.append(_user_to_dict(u, campaign_count, sent_count))
    
    return {
        "users": result,
        "total_users": len(result),
        "blocked_users": sum(1 for u in users if u.is_blocked),
        "admin_users": sum(1 for u in users if u.is_superuser),
    }


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get details of a single user"""
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    campaign_count = db.query(func.count(Campaign.id)).filter(Campaign.user_id == u.id).scalar() or 0
    sent_count = db.query(func.sum(Campaign.sent_count)).filter(Campaign.user_id == u.id).scalar() or 0
    return _user_to_dict(u, campaign_count, sent_count)


@router.put("/users/{user_id}/limit")
async def set_user_limit(
    user_id: int,
    data: SetLimitRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Set / update a user's email sending limit"""
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if data.email_limit < 0:
        raise HTTPException(status_code=400, detail="Limit cannot be negative")
    
    u.email_limit = data.email_limit
    db.commit()
    return {"success": True, "message": f"Limit set to {data.email_limit}", "email_limit": u.email_limit}


@router.post("/users/{user_id}/block")
async def block_user(
    user_id: int,
    data: BlockRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Block or unblock a user's email service"""
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if u.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot block yourself")
    
    u.is_blocked = data.is_blocked
    db.commit()
    return {
        "success": True,
        "message": f"User {'blocked' if data.is_blocked else 'unblocked'}",
        "is_blocked": u.is_blocked
    }


@router.post("/users/{user_id}/reset-usage")
async def reset_usage(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Reset a user's emails_used counter back to 0"""
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.emails_used = 0
    db.commit()
    return {"success": True, "message": "Usage reset to 0"}


@router.post("/users/{user_id}/make-admin")
async def toggle_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Toggle admin (superuser) status for a user"""
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.is_superuser = not u.is_superuser
    db.commit()
    return {"success": True, "is_superuser": u.is_superuser}
