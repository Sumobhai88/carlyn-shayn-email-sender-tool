"""
Analytics business logic service
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime
from typing import Optional

from app.models.email_log import EmailLog
from app.models.campaign import Campaign


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_overview(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        campaign_id: Optional[int] = None
    ) -> dict:
        """Get analytics overview"""
        query = self.db.query(EmailLog)
        
        if campaign_id:
            query = query.filter(EmailLog.campaign_id == campaign_id)
        if start_date:
            query = query.filter(EmailLog.created_at >= start_date)
        if end_date:
            query = query.filter(EmailLog.created_at <= end_date)
        
        total = query.count()
        delivered = query.filter(EmailLog.delivery_status == "delivered").count()
        opened = query.filter(EmailLog.opened == True).count()
        bounced = query.filter(EmailLog.bounced == True).count()
        unsubscribed = query.filter(EmailLog.unsubscribed == True).count()
        
        return {
            "total_sent": total,
            "delivered": delivered,
            "opened": opened,
            "bounced": bounced,
            "unsubscribed": unsubscribed,
            "delivery_rate": (delivered / total * 100) if total > 0 else 0,
            "open_rate": (opened / delivered * 100) if delivered > 0 else 0
        }
    
    async def get_email_logs(
        self,
        skip: int = 0,
        limit: int = 10,
        campaign_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> dict:
        """Get email logs with filters"""
        # Join with Campaign to get campaign_name
        query = self.db.query(
            EmailLog,
            Campaign.campaign_name
        ).join(
            Campaign,
            EmailLog.campaign_id == Campaign.id
        )
        
        if campaign_id:
            query = query.filter(EmailLog.campaign_id == campaign_id)
        
        if status_filter:
            if status_filter == "delivered":
                query = query.filter(EmailLog.delivery_status == "delivered")
            elif status_filter == "opened":
                query = query.filter(EmailLog.opened == True)
            elif status_filter == "bounced":
                query = query.filter(EmailLog.bounced == True)
            elif status_filter == "unsubscribed":
                query = query.filter(EmailLog.unsubscribed == True)
            elif status_filter == "failed":
                query = query.filter(EmailLog.delivery_status == "failed")
        
        if search:
            query = query.filter(
                or_(
                    EmailLog.recipient_email.ilike(f"%{search}%"),
                    EmailLog.subject.ilike(f"%{search}%"),
                    Campaign.campaign_name.ilike(f"%{search}%")
                )
            )
        
        total = query.count()
        results = query.order_by(EmailLog.created_at.desc()).offset(skip).limit(limit).all()
        
        # Transform results to include campaign_name
        email_logs = []
        for email_log, campaign_name in results:
            log_dict = {
                "id": email_log.id,
                "campaign_id": email_log.campaign_id,
                "campaign_name": campaign_name,
                "contact_id": email_log.contact_id,
                "recipient_email": email_log.recipient_email,
                "subject": email_log.subject,
                "delivery_status": email_log.delivery_status,
                "opened": email_log.opened,
                "bounced": email_log.bounced,
                "unsubscribed": email_log.unsubscribed,
                "tracking_id": email_log.tracking_id,
                "sent_at": email_log.sent_at.isoformat() if email_log.sent_at else None,
                "delivered_at": email_log.delivered_at.isoformat() if email_log.delivered_at else None,
                "opened_at": email_log.opened_at.isoformat() if email_log.opened_at else None,
                "created_at": email_log.created_at.isoformat() if email_log.created_at else None,
            }
            email_logs.append(log_dict)
        
        return {
            "total": total,
            "email_logs": email_logs,
            "skip": skip,
            "limit": limit
        }
    
    async def get_stats(self, campaign_id: Optional[int] = None) -> dict:
        """Get detailed statistics"""
        query = self.db.query(EmailLog)
        
        if campaign_id:
            query = query.filter(EmailLog.campaign_id == campaign_id)
        
        total_sent = query.count()
        delivered = query.filter(EmailLog.delivery_status == "delivered").count()
        opened = query.filter(EmailLog.opened == True).count()
        bounced = query.filter(EmailLog.bounced == True).count()
        failed = query.filter(EmailLog.delivery_status == "failed").count()
        unsubscribed = query.filter(EmailLog.unsubscribed == True).count()
        
        return {
            "total_sent": total_sent,
            "delivered": delivered,
            "opened": opened,
            "bounced": bounced,
            "failed": failed,
            "unsubscribed": unsubscribed,
            "delivery_rate": (delivered / total_sent * 100) if total_sent > 0 else 0,
            "open_rate": (opened / delivered * 100) if delivered > 0 else 0
        }
