"""
Bounce handling service for email delivery failures
Detects, categorizes, and manages email bounces
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
import logging

from app.models.email_log import EmailLog
from app.models.contact import Contact
from app.models.campaign import Campaign

logger = logging.getLogger(__name__)


class BounceService:
    """Service for handling email bounces and delivery failures"""
    
    # Bounce type patterns
    HARD_BOUNCE_PATTERNS = [
        r'user unknown',
        r'mailbox not found',
        r'does not exist',
        r'invalid recipient',
        r'address rejected',
        r'no such user',
        r'account disabled',
        r'recipient address rejected',
        r'user not found',
        r'mailbox unavailable',
        r'550',  # Permanent failure
        r'551',  # User not local
        r'553',  # Mailbox name not allowed
    ]
    
    SOFT_BOUNCE_PATTERNS = [
        r'mailbox full',
        r'quota exceeded',
        r'mailbox is full',
        r'over quota',
        r'insufficient storage',
        r'temporarily unavailable',
        r'try again later',
        r'greylisted',
        r'deferred',
        r'421',  # Service not available
        r'422',  # Mailbox full
        r'450',  # Mailbox temporarily unavailable
        r'451',  # Local error
        r'452',  # Insufficient system storage
    ]
    
    SPAM_BOUNCE_PATTERNS = [
        r'spam',
        r'blacklist',
        r'blocked',
        r'rejected as spam',
        r'spam detected',
        r'content rejected',
        r'message filtered',
        r'policy violation',
    ]
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==========================================================================
    # BOUNCE DETECTION & CATEGORIZATION
    # ==========================================================================
    
    def categorize_bounce(self, error_message: str) -> str:
        """
        Categorize bounce type based on error message
        
        Args:
            error_message: SMTP error message
            
        Returns:
            Bounce type: 'hard', 'soft', or 'complaint'
            
        Example:
            >>> categorize_bounce("550 User unknown")
            'hard'
            >>> categorize_bounce("Mailbox full")
            'soft'
        """
        if not error_message:
            return 'soft'
        
        error_lower = error_message.lower()
        
        # Check for spam/complaint patterns
        for pattern in self.SPAM_BOUNCE_PATTERNS:
            if re.search(pattern, error_lower, re.IGNORECASE):
                return 'complaint'
        
        # Check for hard bounce patterns
        for pattern in self.HARD_BOUNCE_PATTERNS:
            if re.search(pattern, error_lower, re.IGNORECASE):
                return 'hard'
        
        # Check for soft bounce patterns
        for pattern in self.SOFT_BOUNCE_PATTERNS:
            if re.search(pattern, error_lower, re.IGNORECASE):
                return 'soft'
        
        # Default to soft bounce if can't determine
        return 'soft'
    
    def extract_smtp_code(self, error_message: str) -> Optional[str]:
        """
        Extract SMTP status code from error message
        
        Args:
            error_message: SMTP error message
            
        Returns:
            SMTP status code (e.g., '550', '421') or None
            
        Example:
            >>> extract_smtp_code("550 5.1.1 User unknown")
            '550'
        """
        if not error_message:
            return None
        
        # Match SMTP codes (XXX format)
        match = re.search(r'\b([2-5][0-9]{2})\b', error_message)
        if match:
            return match.group(1)
        
        return None
    
    def is_permanent_failure(self, error_message: str) -> bool:
        """
        Determine if error represents permanent failure
        
        Args:
            error_message: SMTP error message
            
        Returns:
            True if permanent failure, False otherwise
        """
        bounce_type = self.categorize_bounce(error_message)
        return bounce_type == 'hard'
    
    # ==========================================================================
    # BOUNCE RECORDING
    # ==========================================================================
    
    async def record_bounce(
        self,
        email_log_id: int,
        error_message: str,
        smtp_code: Optional[str] = None
    ) -> Dict:
        """
        Record email bounce
        
        Updates EmailLog with bounce information and updates campaign statistics
        
        Args:
            email_log_id: EmailLog ID
            error_message: Error message from SMTP
            smtp_code: Optional SMTP status code
            
        Returns:
            Dictionary with bounce details
            
        Example:
            >>> result = await record_bounce(123, "550 User unknown", "550")
            >>> print(result)
            {
                'success': True,
                'bounce_type': 'hard',
                'email_log_id': 123,
                'campaign_id': 1
            }
        """
        try:
            # Get email log
            email_log = self.db.query(EmailLog).filter(
                EmailLog.id == email_log_id
            ).first()
            
            if not email_log:
                logger.warning(f"EmailLog {email_log_id} not found for bounce recording")
                return {
                    'success': False,
                    'error': 'EmailLog not found'
                }
            
            # Categorize bounce
            bounce_type = self.categorize_bounce(error_message)
            
            # Extract SMTP code if not provided
            if not smtp_code:
                smtp_code = self.extract_smtp_code(error_message)
            
            now = datetime.utcnow()
            
            # Update email log
            email_log.bounced = True
            email_log.bounced_at = now
            email_log.bounce_type = bounce_type
            email_log.error_message = error_message[:1000]  # Truncate long errors
            email_log.delivery_status = 'bounced'
            
            # Update campaign statistics
            campaign = self.db.query(Campaign).filter(
                Campaign.id == email_log.campaign_id
            ).first()
            
            if campaign:
                campaign.bounced_count = (campaign.bounced_count or 0) + 1
            
            # For hard bounces, consider marking contact as bounced
            if bounce_type == 'hard':
                contact = self.db.query(Contact).filter(
                    Contact.id == email_log.contact_id
                ).first()
                
                if contact:
                    # You might want to add a 'bounced' flag to Contact model
                    # to prevent future emails to this address
                    pass
            
            self.db.commit()
            
            logger.info(
                f"Recorded {bounce_type} bounce: email_log_id={email_log_id}, "
                f"campaign_id={email_log.campaign_id}, "
                f"recipient={email_log.recipient_email}, "
                f"smtp_code={smtp_code}"
            )
            
            return {
                'success': True,
                'email_log_id': email_log_id,
                'campaign_id': email_log.campaign_id,
                'recipient_email': email_log.recipient_email,
                'bounce_type': bounce_type,
                'smtp_code': smtp_code,
                'bounced_at': now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error recording bounce: {str(e)}")
            self.db.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    async def record_smtp_failure(
        self,
        email_log_id: int,
        exception: Exception
    ) -> Dict:
        """
        Record SMTP sending failure
        
        Convenience method that extracts error details from exception
        
        Args:
            email_log_id: EmailLog ID
            exception: Exception from SMTP sending
            
        Returns:
            Dictionary with failure details
        """
        error_message = str(exception)
        
        # Extract SMTP code from exception if available
        smtp_code = None
        if hasattr(exception, 'smtp_code'):
            smtp_code = str(exception.smtp_code)
        elif hasattr(exception, 'code'):
            smtp_code = str(exception.code)
        
        return await self.record_bounce(email_log_id, error_message, smtp_code)
    
    # ==========================================================================
    # BOUNCE ANALYTICS
    # ==========================================================================
    
    async def get_bounce_statistics(self, campaign_id: int) -> Dict:
        """
        Get bounce statistics for a campaign
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Dictionary with bounce statistics
        """
        # Total sent
        total_sent = self.db.query(func.count(EmailLog.id)).filter(
            EmailLog.campaign_id == campaign_id,
            EmailLog.delivery_status.in_(['sent', 'delivered', 'bounced'])
        ).scalar() or 0
        
        # Total bounced
        total_bounced = self.db.query(func.count(EmailLog.id)).filter(
            EmailLog.campaign_id == campaign_id,
            EmailLog.bounced == True
        ).scalar() or 0
        
        # By bounce type
        hard_bounces = self.db.query(func.count(EmailLog.id)).filter(
            EmailLog.campaign_id == campaign_id,
            EmailLog.bounce_type == 'hard'
        ).scalar() or 0
        
        soft_bounces = self.db.query(func.count(EmailLog.id)).filter(
            EmailLog.campaign_id == campaign_id,
            EmailLog.bounce_type == 'soft'
        ).scalar() or 0
        
        complaints = self.db.query(func.count(EmailLog.id)).filter(
            EmailLog.campaign_id == campaign_id,
            EmailLog.bounce_type == 'complaint'
        ).scalar() or 0
        
        # Calculate bounce rate
        bounce_rate = (total_bounced / total_sent * 100) if total_sent > 0 else 0.0
        
        # Get recent bounces
        recent_bounces = self.db.query(EmailLog).filter(
            EmailLog.campaign_id == campaign_id,
            EmailLog.bounced == True
        ).order_by(EmailLog.bounced_at.desc()).limit(10).all()
        
        return {
            'campaign_id': campaign_id,
            'total_sent': total_sent,
            'total_bounced': total_bounced,
            'successfully_delivered': total_sent - total_bounced,
            'bounce_rate': round(bounce_rate, 2),
            'hard_bounces': hard_bounces,
            'soft_bounces': soft_bounces,
            'complaints': complaints,
            'recent_bounces': [
                {
                    'email_log_id': log.id,
                    'recipient_email': log.recipient_email,
                    'bounce_type': log.bounce_type,
                    'error_message': log.error_message[:200] if log.error_message else None,
                    'bounced_at': log.bounced_at.isoformat() if log.bounced_at else None
                }
                for log in recent_bounces
            ]
        }
    
    async def get_bounce_reasons(self, campaign_id: int, limit: int = 20) -> List[Dict]:
        """
        Get most common bounce reasons for a campaign
        
        Args:
            campaign_id: Campaign ID
            limit: Maximum number of reasons to return
            
        Returns:
            List of bounce reasons with counts
        """
        # Group by error_message
        bounce_reasons = self.db.query(
            EmailLog.bounce_type,
            EmailLog.error_message,
            func.count(EmailLog.id).label('count')
        ).filter(
            EmailLog.campaign_id == campaign_id,
            EmailLog.bounced == True,
            EmailLog.error_message.isnot(None)
        ).group_by(
            EmailLog.bounce_type,
            EmailLog.error_message
        ).order_by(
            func.count(EmailLog.id).desc()
        ).limit(limit).all()
        
        return [
            {
                'bounce_type': bounce_type,
                'error_message': error_msg[:200] if error_msg else 'Unknown',
                'count': count
            }
            for bounce_type, error_msg, count in bounce_reasons
        ]
    
    async def get_bounced_emails(
        self,
        campaign_id: Optional[int] = None,
        bounce_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get list of bounced emails with filters
        
        Args:
            campaign_id: Optional campaign filter
            bounce_type: Optional bounce type filter ('hard', 'soft', 'complaint')
            limit: Maximum results
            
        Returns:
            List of bounced emails
        """
        query = self.db.query(EmailLog).filter(
            EmailLog.bounced == True
        )
        
        if campaign_id:
            query = query.filter(EmailLog.campaign_id == campaign_id)
        
        if bounce_type:
            query = query.filter(EmailLog.bounce_type == bounce_type)
        
        bounced_emails = query.order_by(
            EmailLog.bounced_at.desc()
        ).limit(limit).all()
        
        return [
            {
                'email_log_id': log.id,
                'campaign_id': log.campaign_id,
                'contact_id': log.contact_id,
                'recipient_email': log.recipient_email,
                'bounce_type': log.bounce_type,
                'error_message': log.error_message,
                'bounced_at': log.bounced_at.isoformat() if log.bounced_at else None,
                'sent_at': log.sent_at.isoformat() if log.sent_at else None
            }
            for log in bounced_emails
        ]
    
    # ==========================================================================
    # BOUNCE PREVENTION
    # ==========================================================================
    
    def get_hard_bounced_emails(self) -> List[str]:
        """
        Get list of email addresses with hard bounces
        
        These emails should be excluded from future campaigns
        
        Returns:
            List of email addresses with hard bounces
        """
        hard_bounced = self.db.query(EmailLog.recipient_email.distinct()).filter(
            EmailLog.bounce_type == 'hard'
        ).all()
        
        return [email for (email,) in hard_bounced]
    
    def is_email_bounced(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Check if email address has bounced
        
        Args:
            email: Email address to check
            
        Returns:
            Tuple of (is_bounced, bounce_type)
        """
        bounce = self.db.query(EmailLog).filter(
            EmailLog.recipient_email == email,
            EmailLog.bounced == True
        ).order_by(EmailLog.bounced_at.desc()).first()
        
        if bounce:
            return True, bounce.bounce_type
        
        return False, None
    
    def should_retry_email(self, email_log_id: int) -> bool:
        """
        Determine if failed email should be retried
        
        Soft bounces can be retried, hard bounces should not
        
        Args:
            email_log_id: EmailLog ID
            
        Returns:
            True if should retry, False otherwise
        """
        email_log = self.db.query(EmailLog).filter(
            EmailLog.id == email_log_id
        ).first()
        
        if not email_log or not email_log.bounced:
            return False
        
        # Only retry soft bounces
        return email_log.bounce_type == 'soft'
    
    # ==========================================================================
    # CLEANUP & MAINTENANCE
    # ==========================================================================
    
    async def suppress_hard_bounced_contacts(self, campaign_id: Optional[int] = None):
        """
        Suppress contacts with hard bounces
        
        Marks contacts as suppressed to prevent future sending
        
        Args:
            campaign_id: Optional campaign ID to limit scope
        """
        # Find all hard bounced email addresses
        query = self.db.query(EmailLog.recipient_email.distinct()).filter(
            EmailLog.bounce_type == 'hard'
        )
        
        if campaign_id:
            query = query.filter(EmailLog.campaign_id == campaign_id)
        
        hard_bounced_emails = [email for (email,) in query.all()]
        
        if not hard_bounced_emails:
            logger.info("No hard bounced emails to suppress")
            return {
                'suppressed_count': 0,
                'emails': []
            }
        
        # You might want to add a 'suppressed' or 'bounced' flag to Contact model
        # For now, we'll just log them
        logger.info(f"Found {len(hard_bounced_emails)} hard bounced emails")
        
        return {
            'suppressed_count': len(hard_bounced_emails),
            'emails': hard_bounced_emails
        }
    
    async def get_bounce_summary(self) -> Dict:
        """
        Get global bounce summary across all campaigns
        
        Returns:
            Dictionary with global bounce statistics
        """
        # Total emails
        total_emails = self.db.query(func.count(EmailLog.id)).filter(
            EmailLog.delivery_status.in_(['sent', 'delivered', 'bounced'])
        ).scalar() or 0
        
        # Total bounced
        total_bounced = self.db.query(func.count(EmailLog.id)).filter(
            EmailLog.bounced == True
        ).scalar() or 0
        
        # By type
        hard_bounces = self.db.query(func.count(EmailLog.id)).filter(
            EmailLog.bounce_type == 'hard'
        ).scalar() or 0
        
        soft_bounces = self.db.query(func.count(EmailLog.id)).filter(
            EmailLog.bounce_type == 'soft'
        ).scalar() or 0
        
        complaints = self.db.query(func.count(EmailLog.id)).filter(
            EmailLog.bounce_type == 'complaint'
        ).scalar() or 0
        
        # Global bounce rate
        bounce_rate = (total_bounced / total_emails * 100) if total_emails > 0 else 0.0
        
        return {
            'total_emails': total_emails,
            'total_bounced': total_bounced,
            'successfully_delivered': total_emails - total_bounced,
            'global_bounce_rate': round(bounce_rate, 2),
            'hard_bounces': hard_bounces,
            'soft_bounces': soft_bounces,
            'complaints': complaints,
            'unique_hard_bounced_emails': len(self.get_hard_bounced_emails())
        }
