"""
Unsubscribe management service
Handles unsubscribe link generation, processing, and prevention of future emails
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
import secrets
import hashlib
from datetime import datetime
from typing import Optional, Dict, List
import logging

from app.models.email_log import EmailLog
from app.models.contact import Contact
from app.models.campaign import Campaign
from app.core.config import settings

logger = logging.getLogger(__name__)


class UnsubscribeService:
    """Service for managing email unsubscribes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==========================================================================
    # UNSUBSCRIBE TOKEN GENERATION
    # ==========================================================================
    
    def generate_unsubscribe_token(
        self,
        contact_id: int,
        recipient_email: str,
        campaign_id: Optional[int] = None
    ) -> str:
        """
        Generate unique unsubscribe token
        
        Creates a secure, unique token that can't be guessed
        Different from tracking token for security separation
        
        Args:
            contact_id: Contact ID
            recipient_email: Recipient email address
            campaign_id: Optional campaign ID
            
        Returns:
            Unique unsubscribe token (40 characters hex)
            
        Example:
            >>> token = generate_unsubscribe_token(123, "user@example.com", 1)
            >>> print(token)
            'a1b2c3d4e5f6...'  # 40 character hex string
        """
        # Create unique string with salt
        unique_string = (
            f"unsubscribe:{contact_id}:{recipient_email}:"
            f"{campaign_id or 'global'}:{secrets.token_hex(16)}"
        )
        
        # Hash to create fixed-length token
        token = hashlib.sha256(unique_string.encode()).hexdigest()[:40]
        
        logger.debug(f"Generated unsubscribe token for contact {contact_id}")
        return token
    
    def generate_unsubscribe_url(
        self,
        contact_id: int,
        recipient_email: str,
        campaign_id: Optional[int] = None
    ) -> str:
        """
        Generate complete unsubscribe URL
        
        Args:
            contact_id: Contact ID
            recipient_email: Recipient email
            campaign_id: Optional campaign ID
            
        Returns:
            Complete unsubscribe URL
            
        Example:
            >>> url = generate_unsubscribe_url(123, "user@example.com")
            >>> print(url)
            'https://track.carlyshayn.com/unsubscribe/a1b2c3d4e5f6'
        """
        token = self.generate_unsubscribe_token(contact_id, recipient_email, campaign_id)
        
        # Build URL
        tracking_domain = settings.TRACKING_DOMAIN.rstrip('/')
        unsubscribe_url = f"{tracking_domain}/unsubscribe/{token}"
        
        logger.debug(f"Generated unsubscribe URL for contact {contact_id}")
        return unsubscribe_url
    
    # ==========================================================================
    # EMAIL FOOTER INJECTION
    # ==========================================================================
    
    def inject_unsubscribe_link(
        self,
        html_content: str,
        unsubscribe_url: str,
        company_name: str = "Carlyn Shayn Email Engine"
    ) -> str:
        """
        Inject unsubscribe link into email HTML footer
        
        Adds professional unsubscribe footer before closing </body> tag
        
        Args:
            html_content: Original HTML email content
            unsubscribe_url: Unsubscribe URL
            company_name: Company name for footer
            
        Returns:
            HTML content with unsubscribe footer injected
            
        Example:
            >>> html = "<html><body>Content</body></html>"
            >>> result = inject_unsubscribe_link(html, "https://example.com/unsub/xyz")
        """
        # Create unsubscribe footer
        footer_html = f"""
<div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; font-size: 12px; color: #666; text-align: center;">
  <p style="margin: 5px 0;">
    You are receiving this email because you opted in to our mailing list.
  </p>
  <p style="margin: 5px 0;">
    <a href="{unsubscribe_url}" style="color: #666; text-decoration: underline;">Unsubscribe</a> 
    from future emails from {company_name}.
  </p>
  <p style="margin: 5px 0; font-size: 11px; color: #999;">
    {company_name} | Email Automation Platform
  </p>
</div>
"""
        
        # Try to inject before closing </body> tag
        if '</body>' in html_content.lower():
            body_close_index = html_content.lower().rfind('</body>')
            html_with_footer = (
                html_content[:body_close_index] +
                footer_html +
                html_content[body_close_index:]
            )
        else:
            # No body tag, append at the end
            html_with_footer = html_content + footer_html
        
        logger.debug("Injected unsubscribe footer into email HTML")
        return html_with_footer
    
    def inject_unsubscribe_plaintext(
        self,
        plain_content: str,
        unsubscribe_url: str,
        company_name: str = "Carlyn Shayn Email Engine"
    ) -> str:
        """
        Add unsubscribe link to plain text email
        
        Args:
            plain_content: Original plain text content
            unsubscribe_url: Unsubscribe URL
            company_name: Company name
            
        Returns:
            Plain text with unsubscribe information
        """
        footer_text = f"""

---

You are receiving this email because you opted in to our mailing list.

To unsubscribe from future emails, visit:
{unsubscribe_url}

{company_name} | Email Automation Platform
"""
        
        return plain_content + footer_text
    
    # ==========================================================================
    # UNSUBSCRIBE PROCESSING
    # ==========================================================================
    
    async def process_unsubscribe(
        self,
        unsubscribe_token: str,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict:
        """
        Process unsubscribe request
        
        Updates Contact and all associated EmailLog entries
        Marks contact as unsubscribed to prevent future emails
        
        Args:
            unsubscribe_token: Unique unsubscribe token
            reason: Optional unsubscribe reason
            ip_address: Client IP address (optional)
            
        Returns:
            Dictionary with success status and details
            
        Example:
            >>> result = await process_unsubscribe("a1b2c3d4e5f6")
            >>> print(result)
            {
                'success': True,
                'contact_id': 123,
                'email': 'user@example.com',
                'unsubscribed_at': '2024-06-17T10:30:00Z'
            }
        """
        try:
            # Find contact by token
            # Note: We need to store token or create a mapping
            # For now, we'll use a different approach - search by email if provided
            
            # Since we can't reliably reverse the token, we'll need to:
            # 1. Store token in Contact table, OR
            # 2. Use email parameter in unsubscribe URL
            # For this implementation, we'll add unsubscribe_token to Contact
            
            contact = self._find_contact_by_unsubscribe_token(unsubscribe_token)
            
            if not contact:
                logger.warning(f"Contact not found for unsubscribe token: {unsubscribe_token[:8]}...")
                return {
                    'success': False,
                    'error': 'Invalid unsubscribe token'
                }
            
            # Check if already unsubscribed
            if contact.unsubscribed:
                logger.info(f"Contact {contact.id} already unsubscribed")
                return {
                    'success': True,
                    'contact_id': contact.id,
                    'email': contact.email,
                    'already_unsubscribed': True,
                    'unsubscribed_at': contact.unsubscribed_at.isoformat() if contact.unsubscribed_at else None
                }
            
            now = datetime.utcnow()
            
            # Update contact
            contact.unsubscribed = True
            contact.unsubscribed_at = now
            if reason:
                contact.unsubscribe_reason = reason
            
            # Update all email logs for this contact
            self.db.query(EmailLog).filter(
                EmailLog.contact_id == contact.id
            ).update({
                'unsubscribed': True,
                'unsubscribed_at': now
            })
            
            # Update campaign unsubscribe counts
            # Get all campaigns for this contact
            campaign_ids = self.db.query(EmailLog.campaign_id.distinct()).filter(
                EmailLog.contact_id == contact.id
            ).all()
            
            for (campaign_id,) in campaign_ids:
                campaign = self.db.query(Campaign).filter(
                    Campaign.id == campaign_id
                ).first()
                
                if campaign:
                    campaign.unsubscribed_count = (campaign.unsubscribed_count or 0) + 1
            
            self.db.commit()
            
            logger.info(
                f"Processed unsubscribe: contact_id={contact.id}, "
                f"email={contact.email}, reason={reason}"
            )
            
            return {
                'success': True,
                'contact_id': contact.id,
                'email': contact.email,
                'unsubscribed_at': now.isoformat(),
                'reason': reason,
                'ip_address': ip_address,
                'already_unsubscribed': False
            }
            
        except Exception as e:
            logger.error(f"Error processing unsubscribe: {str(e)}")
            self.db.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_contact_by_unsubscribe_token(self, token: str) -> Optional[Contact]:
        """
        Find contact by unsubscribe token
        
        Note: Requires unsubscribe_token column in Contact table
        
        Args:
            token: Unsubscribe token
            
        Returns:
            Contact if found, None otherwise
        """
        # This will work once we add unsubscribe_token to Contact model
        contact = self.db.query(Contact).filter(
            Contact.unsubscribe_token == token
        ).first()
        
        return contact
    
    # ==========================================================================
    # UNSUBSCRIBE PREVENTION
    # ==========================================================================
    
    def is_unsubscribed(self, contact_id: int) -> bool:
        """
        Check if contact is unsubscribed
        
        Args:
            contact_id: Contact ID
            
        Returns:
            True if unsubscribed, False otherwise
        """
        contact = self.db.query(Contact).filter(
            Contact.id == contact_id
        ).first()
        
        return contact.unsubscribed if contact else False
    
    def is_email_unsubscribed(self, email: str) -> bool:
        """
        Check if email address is unsubscribed
        
        Args:
            email: Email address
            
        Returns:
            True if unsubscribed, False otherwise
        """
        contact = self.db.query(Contact).filter(
            Contact.email == email,
            Contact.unsubscribed == True
        ).first()
        
        return contact is not None
    
    def filter_unsubscribed_contacts(
        self,
        contact_ids: List[int]
    ) -> List[int]:
        """
        Filter out unsubscribed contacts from list
        
        Args:
            contact_ids: List of contact IDs
            
        Returns:
            List of contact IDs (excluding unsubscribed)
        """
        subscribed_contacts = self.db.query(Contact.id).filter(
            Contact.id.in_(contact_ids),
            or_(Contact.unsubscribed == False, Contact.unsubscribed.is_(None))
        ).all()
        
        return [contact_id for (contact_id,) in subscribed_contacts]
    
    # ==========================================================================
    # STATISTICS
    # ==========================================================================
    
    async def get_unsubscribe_statistics(self, campaign_id: int) -> Dict:
        """
        Get unsubscribe statistics for a campaign
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Dictionary with unsubscribe statistics
        """
        # Total recipients
        total_recipients = self.db.query(func.count(Contact.id)).filter(
            Contact.campaign_id == campaign_id
        ).scalar() or 0
        
        # Total unsubscribed
        total_unsubscribed = self.db.query(func.count(Contact.id)).filter(
            Contact.campaign_id == campaign_id,
            Contact.unsubscribed == True
        ).scalar() or 0
        
        # Calculate unsubscribe rate
        unsubscribe_rate = (total_unsubscribed / total_recipients * 100) if total_recipients > 0 else 0.0
        
        # Get recent unsubscribes
        recent_unsubscribes = self.db.query(Contact).filter(
            Contact.campaign_id == campaign_id,
            Contact.unsubscribed == True
        ).order_by(Contact.unsubscribed_at.desc()).limit(10).all()
        
        return {
            'campaign_id': campaign_id,
            'total_recipients': total_recipients,
            'total_unsubscribed': total_unsubscribed,
            'still_subscribed': total_recipients - total_unsubscribed,
            'unsubscribe_rate': round(unsubscribe_rate, 2),
            'recent_unsubscribes': [
                {
                    'contact_id': c.id,
                    'email': c.email,
                    'unsubscribed_at': c.unsubscribed_at.isoformat() if c.unsubscribed_at else None,
                    'reason': getattr(c, 'unsubscribe_reason', None)
                }
                for c in recent_unsubscribes
            ]
        }
    
    async def get_global_unsubscribe_stats(self) -> Dict:
        """
        Get global unsubscribe statistics
        
        Returns:
            Dictionary with global statistics
        """
        # Total contacts
        total_contacts = self.db.query(func.count(Contact.id)).scalar() or 0
        
        # Total unsubscribed
        total_unsubscribed = self.db.query(func.count(Contact.id)).filter(
            Contact.unsubscribed == True
        ).scalar() or 0
        
        # Unsubscribe rate
        unsubscribe_rate = (total_unsubscribed / total_contacts * 100) if total_contacts > 0 else 0.0
        
        # Unsubscribes by date (last 7 days)
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_unsubs = self.db.query(func.count(Contact.id)).filter(
            Contact.unsubscribed == True,
            Contact.unsubscribed_at >= seven_days_ago
        ).scalar() or 0
        
        return {
            'total_contacts': total_contacts,
            'total_unsubscribed': total_unsubscribed,
            'still_subscribed': total_contacts - total_unsubscribed,
            'global_unsubscribe_rate': round(unsubscribe_rate, 2),
            'unsubscribes_last_7_days': recent_unsubs
        }
    
    # ==========================================================================
    # BATCH OPERATIONS
    # ==========================================================================
    
    def prepare_email_with_unsubscribe(
        self,
        contact_id: int,
        recipient_email: str,
        campaign_id: int,
        html_content: str,
        plain_content: Optional[str] = None,
        company_name: str = "Carlyn Shayn Email Engine"
    ) -> Dict[str, str]:
        """
        Prepare email with unsubscribe link injected
        
        Args:
            contact_id: Contact ID
            recipient_email: Recipient email
            campaign_id: Campaign ID
            html_content: HTML email content
            plain_content: Optional plain text content
            company_name: Company name for footer
            
        Returns:
            Dictionary with HTML, plain text, and unsubscribe URL
        """
        # Generate unsubscribe URL
        unsubscribe_url = self.generate_unsubscribe_url(
            contact_id,
            recipient_email,
            campaign_id
        )
        
        # Inject unsubscribe link
        html_with_unsub = self.inject_unsubscribe_link(
            html_content,
            unsubscribe_url,
            company_name
        )
        
        # Handle plain text if provided
        plain_with_unsub = None
        if plain_content:
            plain_with_unsub = self.inject_unsubscribe_plaintext(
                plain_content,
                unsubscribe_url,
                company_name
            )
        
        return {
            'html': html_with_unsub,
            'plain': plain_with_unsub,
            'unsubscribe_url': unsubscribe_url
        }
