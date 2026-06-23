"""
Campaign progress tracking service
Provides real-time progress data for frontend polling
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.email_log import EmailLog
from app.schemas.progress import (
    CampaignProgressResponse,
    BulkProgressResponse
)
from app.core.exceptions import CampaignNotFoundError

logger = logging.getLogger(__name__)


class ProgressService:
    """Service for tracking campaign progress"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==========================================================================
    # PROGRESS CALCULATION
    # ==========================================================================
    
    async def get_campaign_progress(self, campaign_id: int) -> CampaignProgressResponse:
        """
        Get real-time progress for a campaign
        
        Calculates:
        - Email counts (sent, delivered, failed, pending)
        - Progress percentage
        - Delivery/Open/Bounce rates
        - Sending speed (emails per minute)
        - Time estimates (elapsed, remaining)
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Real-time campaign progress data
            
        Raises:
            CampaignNotFoundError: If campaign doesn't exist
        """
        # Get campaign
        campaign = self.db.query(Campaign).filter(
            Campaign.id == campaign_id
        ).first()
        
        if not campaign:
            logger.warning(f"Campaign not found: ID {campaign_id}")
            raise CampaignNotFoundError(campaign_id)
        
        # Get counts from database (most accurate)
        total_emails = campaign.total_emails or 0
        sent_count = campaign.sent_count or 0
        delivered_count = campaign.delivered_count or 0
        failed_count = self._get_failed_count(campaign_id)
        pending_count = max(0, total_emails - sent_count)
        
        # Additional metrics
        opened_count = campaign.opened_count or 0
        bounced_count = campaign.bounced_count or 0
        unsubscribed_count = campaign.unsubscribed_count or 0
        
        # Calculate percentage
        percentage = self._calculate_percentage(sent_count, total_emails)
        
        # Calculate rates
        delivery_rate = self._calculate_rate(delivered_count, sent_count)
        open_rate = self._calculate_rate(opened_count, delivered_count)
        bounce_rate = self._calculate_rate(bounced_count, sent_count)
        
        # Time calculations
        started_at = campaign.started_at
        completed_at = campaign.completed_at
        
        time_elapsed_seconds = 0
        emails_per_minute = 0.0
        time_remaining_seconds = 0
        estimated_completion = None
        
        if started_at:
            # Calculate elapsed time
            now = datetime.utcnow()
            if completed_at:
                elapsed = (completed_at - started_at).total_seconds()
            else:
                elapsed = (now - started_at).total_seconds()
            
            time_elapsed_seconds = int(elapsed)
            
            # Calculate sending speed (emails per minute)
            if elapsed > 0:
                emails_per_minute = (sent_count / elapsed) * 60
            
            # Estimate remaining time
            if emails_per_minute > 0 and pending_count > 0:
                time_remaining_seconds = int((pending_count / emails_per_minute) * 60)
                estimated_completion = now + timedelta(seconds=time_remaining_seconds)
        
        # Status indicators
        is_active = campaign.status in ['running', 'sending']
        is_completed = campaign.status == 'completed'
        has_errors = failed_count > 0 or campaign.status == 'failed'
        
        # Build response
        progress = CampaignProgressResponse(
            campaign_id=campaign.id,
            campaign_name=campaign.campaign_name,
            status=campaign.status,
            total_emails=total_emails,
            sent_count=sent_count,
            delivered_count=delivered_count,
            failed_count=failed_count,
            pending_count=pending_count,
            opened_count=opened_count,
            bounced_count=bounced_count,
            unsubscribed_count=unsubscribed_count,
            percentage=percentage,
            delivery_rate=delivery_rate,
            open_rate=open_rate,
            bounce_rate=bounce_rate,
            started_at=started_at,
            estimated_completion=estimated_completion,
            completed_at=completed_at,
            emails_per_minute=round(emails_per_minute, 2),
            time_elapsed_seconds=time_elapsed_seconds,
            time_remaining_seconds=time_remaining_seconds,
            is_active=is_active,
            is_completed=is_completed,
            has_errors=has_errors,
            last_updated=datetime.utcnow()
        )
        
        logger.debug(
            f"Progress for campaign {campaign_id}: "
            f"{sent_count}/{total_emails} ({percentage:.1f}%)"
        )
        
        return progress
    
    # ==========================================================================
    # BULK OPERATIONS
    # ==========================================================================
    
    async def get_all_progress(
        self,
        active_only: bool = False,
        limit: int = 50
    ) -> BulkProgressResponse:
        """
        Get progress for multiple campaigns
        
        Args:
            active_only: Only return active campaigns
            limit: Maximum number of campaigns
            
        Returns:
            Bulk progress data
        """
        query = self.db.query(Campaign)
        
        if active_only:
            query = query.filter(Campaign.status.in_(['running', 'sending', 'paused']))
        
        campaigns = query.order_by(Campaign.created_at.desc()).limit(limit).all()
        
        # Get progress for each campaign
        progress_list = []
        active_count = 0
        
        for campaign in campaigns:
            try:
                progress = await self.get_campaign_progress(campaign.id)
                progress_list.append(progress)
                
                if progress.is_active:
                    active_count += 1
            except Exception as e:
                logger.error(f"Error getting progress for campaign {campaign.id}: {str(e)}")
                continue
        
        return BulkProgressResponse(
            total_campaigns=len(progress_list),
            active_campaigns=active_count,
            campaigns=progress_list,
            last_updated=datetime.utcnow()
        )
    
    # ==========================================================================
    # PROGRESS UPDATES
    # ==========================================================================
    
    async def update_progress(
        self,
        campaign_id: int,
        sent_count: Optional[int] = None,
        delivered_count: Optional[int] = None,
        failed_count: Optional[int] = None,
        status: Optional[str] = None
    ):
        """
        Update campaign progress
        Called by email sender during campaign execution
        
        Args:
            campaign_id: Campaign ID
            sent_count: Update sent count
            delivered_count: Update delivered count
            failed_count: Update failed count
            status: Update campaign status
        """
        campaign = self.db.query(Campaign).filter(
            Campaign.id == campaign_id
        ).first()
        
        if not campaign:
            raise CampaignNotFoundError(campaign_id)
        
        # Update counts
        if sent_count is not None:
            campaign.sent_count = sent_count
        
        if delivered_count is not None:
            campaign.delivered_count = delivered_count
        
        if status is not None:
            campaign.status = status
            
            # Set timestamps based on status
            if status == 'running' and not campaign.started_at:
                campaign.started_at = datetime.utcnow()
            
            if status == 'completed' and not campaign.completed_at:
                campaign.completed_at = datetime.utcnow()
        
        self.db.commit()
        logger.debug(f"Updated progress for campaign {campaign_id}")
    
    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================
    
    def _get_failed_count(self, campaign_id: int) -> int:
        """Get failed email count from email logs"""
        failed = self.db.query(func.count(EmailLog.id)).filter(
            EmailLog.campaign_id == campaign_id,
            EmailLog.delivery_status == 'failed'
        ).scalar()
        
        return failed or 0
    
    def _calculate_percentage(self, sent: int, total: int) -> float:
        """Calculate progress percentage"""
        if total == 0:
            return 0.0
        return round((sent / total) * 100, 2)
    
    def _calculate_rate(self, numerator: int, denominator: int) -> float:
        """Calculate rate percentage"""
        if denominator == 0:
            return 0.0
        return round((numerator / denominator) * 100, 2)
    
    # ==========================================================================
    # REAL-TIME STATISTICS
    # ==========================================================================
    
    async def get_live_stats(self, campaign_id: int) -> dict:
        """
        Get live statistics directly from email logs
        Most accurate but slower - use sparingly
        
        Returns:
            Dictionary with live counts
        """
        # Count by delivery status
        stats = self.db.query(
            EmailLog.delivery_status,
            func.count(EmailLog.id).label('count')
        ).filter(
            EmailLog.campaign_id == campaign_id
        ).group_by(
            EmailLog.delivery_status
        ).all()
        
        # Build stats dictionary
        status_counts = {status: count for status, count in stats}
        
        return {
            'sent': status_counts.get('sent', 0) + status_counts.get('delivered', 0),
            'delivered': status_counts.get('delivered', 0),
            'failed': status_counts.get('failed', 0),
            'pending': status_counts.get('pending', 0),
            'bounced': self.db.query(func.count(EmailLog.id)).filter(
                EmailLog.campaign_id == campaign_id,
                EmailLog.bounced == True
            ).scalar() or 0,
            'opened': self.db.query(func.count(EmailLog.id)).filter(
                EmailLog.campaign_id == campaign_id,
                EmailLog.opened == True
            ).scalar() or 0
        }
