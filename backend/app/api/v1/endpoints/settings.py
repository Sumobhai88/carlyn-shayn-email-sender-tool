"""
Settings & Notifications endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.notification import Notification

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None


class NotifPrefsUpdate(BaseModel):
    notif_email: Optional[bool] = None
    notif_campaigns: Optional[bool] = None


# ── Profile Settings ─────────────────────────────────────────────────────────

@router.get("/profile")
async def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user profile settings"""
    return {
        "id": current_user.id,
        "name": current_user.name or "",
        "email": current_user.email,
        "picture": current_user.picture,
        "company_name": current_user.company_name or "",
        "notif_email": current_user.notif_email if current_user.notif_email is not None else True,
        "notif_campaigns": current_user.notif_campaigns if current_user.notif_campaigns is not None else True,
        "is_superuser": current_user.is_superuser,
        "email_limit": current_user.email_limit if current_user.email_limit is not None else 1000,
        "emails_used": current_user.emails_used if current_user.emails_used is not None else 0,
        "is_blocked": current_user.is_blocked if current_user.is_blocked is not None else False,
    }


@router.get("/usage")
async def get_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's email usage and limit"""
    limit = current_user.email_limit if current_user.email_limit is not None else 1000
    used = current_user.emails_used if current_user.emails_used is not None else 0
    return {
        "email_limit": limit,
        "emails_used": used,
        "remaining": max(0, limit - used),
        "percentage_used": round((used / limit * 100), 1) if limit > 0 else 0,
        "is_blocked": current_user.is_blocked if current_user.is_blocked is not None else False,
    }


@router.put("/profile")
async def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user profile"""
    if data.name is not None:
        current_user.name = data.name
    if data.company_name is not None:
        current_user.company_name = data.company_name
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "success": True,
        "name": current_user.name,
        "company_name": current_user.company_name,
        "message": "Profile updated successfully"
    }


@router.put("/notifications/preferences")
async def update_notif_prefs(
    data: NotifPrefsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update notification preferences"""
    if data.notif_email is not None:
        current_user.notif_email = data.notif_email
    if data.notif_campaigns is not None:
        current_user.notif_campaigns = data.notif_campaigns
    
    db.commit()
    return {"success": True, "message": "Notification preferences updated"}


# ── Notifications ─────────────────────────────────────────────────────────────

@router.get("/notifications")
async def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notifications for current user"""
    notifs = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {
        "notifications": [
            {
                "id": n.id,
                "type": n.type,
                "title": n.title,
                "message": n.message,
                "is_read": n.is_read,
                "campaign_id": n.campaign_id,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "time": _time_ago(n.created_at)
            }
            for n in notifs
        ],
        "unread_count": unread_count
    }


@router.post("/notifications/{notif_id}/read")
async def mark_as_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a single notification as read"""
    notif = db.query(Notification).filter(
        Notification.id == notif_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notif.is_read = True
    db.commit()
    return {"success": True}


@router.post("/notifications/read-all")
async def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"success": True, "message": "All notifications marked as read"}


@router.delete("/notifications/{notif_id}")
async def delete_notification(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a notification"""
    notif = db.query(Notification).filter(
        Notification.id == notif_id,
        Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notif)
    db.commit()
    return {"success": True}


# ── Helper ────────────────────────────────────────────────────────────────────

def _time_ago(dt) -> str:
    if not dt:
        return ""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = int((now - dt).total_seconds())
    if diff < 60:
        return "Just now"
    elif diff < 3600:
        return f"{diff // 60}m ago"
    elif diff < 86400:
        return f"{diff // 3600}h ago"
    else:
        return f"{diff // 86400}d ago"
