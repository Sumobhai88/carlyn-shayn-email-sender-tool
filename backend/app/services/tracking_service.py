"""
Email tracking service for open tracking and engagement monitoring
Uses tracking pixels and unique tokens for each recipient
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
import secrets
import hashlib
from datetime import datetime
from typing import Optional, Dict
import logging

from app.models.email_log import EmailLog
from app.models.campaign import Campaign
from app.core.config import settings

logger = logging.getLogger(__name__)


class TrackingService:
    """Service for email tracking and engagement monitoring"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==========================================================================
    # TRACKING TOKEN GENERATION
    # ==========================================================================
    
    def generate_tracking_token(
        self,
        email_log_id: int,
        recipient_email: str,
        campaign_id: int
    ) -> str:
        """
        Generate unique tracking token for a specific email
        
        Creates a secure, unique token that can't be guessed or replayed
        
        Args:
            email_log_id: Email log ID
            recipient_email: Recipient email address
            campaign_id: Campaign ID
            
        Returns:
            Unique tracking token (32 characters hex)
            
        Example:
            >>> token = generate_tracking_token(123, "user@example.com", 1)
            >>> print(token)
            'a1b2c3d4e5f6...'  # 32 character hex string
        """
        # Create unique string from components
        unique_string = f"{email_log_id}:{recipient_email}:{campaign_id}:{secrets.token_hex(8)}"
        
        # Hash it to create fixed-length token
        token = hashlib.sha256(unique_string.encode()).hexdigest()[:32]
        
        logger.debug(f"Generated tracking token for email_log {email_log_id}")
        return token
    
    def generate_tracking_pixel_url(
        self,
        email_log_id: int,
        recipient_email: str,
        campaign_id: int
    ) -> str:
        """
        Generate complete tracking pixel URL
        
        Args:
            email_log_id: Email log ID
            recipient_email: Recipient email
            campaign_id: Campaign ID
            
        Returns:
            Complete tracking pixel URL
            
        Example:
            >>> url = generate_tracking_pixel_url(123, "user@example.com", 1)
            >>> print(url)
            'https://track.carlyshayn.com/track/a1b2c3d4e5f6'
        """
        token = self.generate_tracking_token(email_log_id, recipient_email, campaign_id)
        
        # Build URL
        tracking_domain = settings.TRACKING_DOMAIN.rstrip('/')
        tracking_url = f"{tracking_domain}/track/{token}"
        
        logger.debug(f"Generated tracking URL: {tracking_url}")
        return tracking_url
    
    # ==========================================================================
    # HTML INJECTION
    # ==========================================================================
    
    def inject_tracking_pixel(
        self,
        html_content: str,
        tracking_url: str
    ) -> str:
        """
        Inject tracking pixel into HTML email content
        
        Adds invisible 1x1 pixel image at the end of email body
        
        Args:
            html_content: Original HTML email content
            tracking_url: Tracking pixel URL
            
        Returns:
            HTML content with tracking pixel injected
            
        Example:
            >>> html = "<html><body>Hello World</body></html>"
            >>> tracked = inject_tracking_pixel(html, "https://track.example.com/xyz")
            >>> print(tracked)
            '<html><body>Hello World<img src="..." /></body></html>'
        """
        # Create tracking pixel HTML
        tracking_pixel = (
            f'<img src="{tracking_url}" '
            f'width="1" height="1" '
            f'style="display:none;" '
            f'alt="" />'
        )
        
        # Try to inject before closing </body> tag
        if '</body>' in html_content.lower():
            # Find last occurrence of </body>
            body_close_index = html_content.lower().rfind('</body>')
            tracked_html = (
                html_content[:body_close_index] +
                tracking_pixel +
                html_content[body_close_index:]
            )
        else:
            # No body tag, append at the end
            tracked_html = html_content + tracking_pixel
        
        logger.debug("Injected tracking pixel into email HTML")
        return tracked_html
    
    def inject_tracking_pixel_plaintext(
        self,
        plain_content: str,
        tracking_url: str
    ) -> str:
        """
        Inject tracking URL into plain text email
        
        Adds tracking link at the bottom of plain text emails
        Note: Plain text tracking is less reliable than HTML
        
        Args:
            plain_content: Original plain text content
            tracking_url: Tracking URL
            
        Returns:
            Plain text with tracking link
        """
        tracking_text = f"\n\n---\nTracking: {tracking_url}"
        return plain_content + tracking_text
    
    # ==========================================================================
    # TRACKING RECORDING
    # ==========================================================================
    
    async def record_email_open(
        self,
        tracking_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict:
        """
        Record email open event
        
        Updates EmailLog with opened=True and opened_at timestamp
        Also updates Campaign opened_count
        Handles repeat opens by incrementing open_count
        
        Args:
            tracking_token: Unique tracking token from pixel URL
            ip_address: Client IP address (optional)
            user_agent: Client user agent string (optional)
            
        Returns:
            Dictionary with success status and details
            
        Example:
            >>> result = await record_email_open("a1b2c3d4e5f6", "192.168.1.1", "Mozilla/5.0...")
            >>> print(result)
            {
                'success': True,
                'email_log_id': 123,
                'campaign_id': 1,
                'first_open': True,
                'opened_at': '2024-06-17T10:30:00Z'
            }
        """
        try:
            # Find email log by tracking token
            email_log = self._find_email_log_by_token(tracking_token)
            
            if not email_log:
                logger.warning(f"Email log not found for token: {tracking_token[:8]}...")
                return {
                    'success': False,
                    'error': 'Invalid tracking token'
                }
            
            # Check if this is the first open
            first_open = not email_log.opened
            
            now = datetime.utcnow()
            
            # Update email log
            if first_open:
                # First open - set all initial values
                email_log.opened = True
                email_log.opened_at = now
                email_log.last_opened_at = now
                email_log.open_count = 1
                
                # Store IP and user agent
                if ip_address:
                    email_log.ip_address = ip_address
                if user_agent:
                    email_log.user_agent = user_agent[:500]  # Truncate if too long
                
                # Update campaign opened_count
                campaign = self.db.query(Campaign).filter(
                    Campaign.id == email_log.campaign_id
                ).first()
                
                if campaign:
                    campaign.opened_count = (campaign.opened_count or 0) + 1
                
                self.db.commit()
                
                logger.info(
                    f"Recorded first email open: email_log_id={email_log.id}, "
                    f"campaign_id={email_log.campaign_id}, "
                    f"recipient={email_log.recipient_email}"
                )
            else:
                # Repeat open - update last_opened_at and increment counter
                email_log.last_opened_at = now
                email_log.open_count = (email_log.open_count or 1) + 1
                
                self.db.commit()
                
                logger.debug(
                    f"Recorded repeat email open #{email_log.open_count}: "
                    f"email_log_id={email_log.id}"
                )
            
            return {
                'success': True,
                'email_log_id': email_log.id,
                'campaign_id': email_log.campaign_id,
                'recipient_email': email_log.recipient_email,
                'first_open': first_open,
                'open_count': email_log.open_count,
                'opened_at': email_log.opened_at.isoformat() if email_log.opened_at else None,
                'last_opened_at': email_log.last_opened_at.isoformat() if email_log.last_opened_at else None
            }
            
        except Exception as e:
            logger.error(f"Error recording email open: {str(e)}")
            self.db.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_email_log_by_token(self, tracking_token: str) -> Optional[EmailLog]:
        """
        Find email log by tracking token
        
        Args:
            tracking_token: Tracking token to lookup
            
        Returns:
            EmailLog if found, None otherwise
        """
        email_log = self.db.query(EmailLog).filter(
            EmailLog.tracking_id == tracking_token
        ).first()
        
        return email_log
    
    # ==========================================================================
    # ANALYTICS
    # ==========================================================================
    
    async def get_open_statistics(self, campaign_id: int) -> Dict:
        """
        Get email open statistics for a campaign
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Dictionary with open statistics
        """
        # Total emails sent
        total_sent = self.db.query(func.count(EmailLog.id)).filter(
            EmailLog.campaign_id == campaign_id,
            EmailLog.delivery_status == 'delivered'
        ).scalar() or 0
        
        # Total opened
        total_opened = self.db.query(func.count(EmailLog.id)).filter(
            EmailLog.campaign_id == campaign_id,
            EmailLog.opened == True
        ).scalar() or 0
        
        # Calculate open rate
        open_rate = (total_opened / total_sent * 100) if total_sent > 0 else 0.0
        
        # Get first and last open times
        first_open = self.db.query(func.min(EmailLog.opened_at)).filter(
            EmailLog.campaign_id == campaign_id,
            EmailLog.opened == True
        ).scalar()
        
        last_open = self.db.query(func.max(EmailLog.opened_at)).filter(
            EmailLog.campaign_id == campaign_id,
            EmailLog.opened == True
        ).scalar()
        
        return {
            'campaign_id': campaign_id,
            'total_sent': total_sent,
            'total_opened': total_opened,
            'not_opened': total_sent - total_opened,
            'open_rate': round(open_rate, 2),
            'first_open': first_open.isoformat() if first_open else None,
            'last_open': last_open.isoformat() if last_open else None
        }
    
    async def get_recent_opens(
        self,
        campaign_id: Optional[int] = None,
        limit: int = 50
    ) -> list:
        """
        Get recent email opens
        
        Args:
            campaign_id: Optional campaign ID filter
            limit: Maximum number of results
            
        Returns:
            List of recent email opens
        """
        query = self.db.query(EmailLog).filter(
            EmailLog.opened == True
        )
        
        if campaign_id:
            query = query.filter(EmailLog.campaign_id == campaign_id)
        
        recent_opens = query.order_by(
            EmailLog.opened_at.desc()
        ).limit(limit).all()
        
        return [
            {
                'email_log_id': log.id,
                'campaign_id': log.campaign_id,
                'recipient_email': log.recipient_email,
                'opened_at': log.opened_at.isoformat() if log.opened_at else None,
                'sent_at': log.sent_at.isoformat() if log.sent_at else None
            }
            for log in recent_opens
        ]
    
    # ==========================================================================
    # BATCH OPERATIONS
    # ==========================================================================
    
    def prepare_email_with_tracking(
        self,
        email_log_id: int,
        recipient_email: str,
        campaign_id: int,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Prepare email with tracking pixel injected
        
        Args:
            email_log_id: Email log ID
            recipient_email: Recipient email
            campaign_id: Campaign ID
            html_content: HTML email content
            plain_content: Optional plain text content
            
        Returns:
            Dictionary with tracked HTML and plain text
        """
        # Generate tracking URL
        tracking_url = self.generate_tracking_pixel_url(
            email_log_id,
            recipient_email,
            campaign_id
        )
        
        # Inject tracking pixel
        tracked_html = self.inject_tracking_pixel(html_content, tracking_url)
        
        # Handle plain text if provided
        tracked_plain = None
        if plain_content:
            # For plain text, we typically don't add tracking
            # But you can optionally add a tracking URL at the bottom
            tracked_plain = plain_content  # No tracking for plain text
        
        return {
            'html': tracked_html,
            'plain': tracked_plain,
            'tracking_url': tracking_url
        }
