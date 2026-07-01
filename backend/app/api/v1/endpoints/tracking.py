"""
Tracking endpoints for email opens and clicks
"""
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.db.database import get_db
from app.services.tracking_service import TrackingService

router = APIRouter()

# 1x1 transparent pixel for email tracking
TRACKING_PIXEL_PATH = Path(__file__).parent.parent.parent.parent / "tracking_pixel.gif"


@router.get("/open/{tracking_id}")
async def track_email_open(
    tracking_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Track email opens via tracking pixel
    
    When recipient opens email, their email client loads the tracking pixel image,
    triggering this endpoint which records the open event.
    """
    service = TrackingService(db)
    
    # Get client info
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Record the open event
    await service.record_email_open(
        tracking_token=tracking_id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # Return 1x1 transparent GIF
    # If pixel file doesn't exist, return empty response
    if TRACKING_PIXEL_PATH.exists():
        return FileResponse(
            TRACKING_PIXEL_PATH,
            media_type="image/gif",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    else:
        # Return minimal GIF bytes directly
        gif_bytes = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        return Response(
            content=gif_bytes,
            media_type="image/gif",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )


@router.get("/click/{tracking_id}")
async def track_email_click(
    tracking_id: str,
    url: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Track link clicks and redirect"""
    from app.models.email_log import EmailLog
    from datetime import datetime, timezone
    
    email_log = db.query(EmailLog).filter(EmailLog.tracking_id == tracking_id).first()
    if email_log:
        db.commit()
    
    return RedirectResponse(url=url, status_code=302)


@router.get("/stats/{tracking_id}")
async def get_tracking_stats(
    tracking_id: str,
    db: Session = Depends(get_db)
):
    """
    Get tracking statistics for a specific email
    """
    from app.models.email_log import EmailLog
    
    email_log = db.query(EmailLog).filter(
        EmailLog.tracking_id == tracking_id
    ).first()
    
    if not email_log:
        return {"error": "Tracking ID not found"}
    
    return {
        "tracking_id": tracking_id,
        "recipient_email": email_log.recipient_email,
        "sent_at": email_log.sent_at.isoformat() if email_log.sent_at else None,
        "opened": email_log.opened,
        "opened_at": email_log.opened_at.isoformat() if email_log.opened_at else None,
        "open_count": getattr(email_log, 'open_count', 0),
        "clicked": getattr(email_log, 'clicked', False),
        "clicked_at": getattr(email_log, 'clicked_at', None),
        "delivery_status": email_log.delivery_status
    }
