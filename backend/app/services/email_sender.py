"""
Email sending service with SMTP integration, connection reuse, and retry logic.
"""
from sqlalchemy.orm import Session
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
import logging
import asyncio
from typing import Optional
from datetime import datetime, timezone

from app.models.smtp_profile import SMTPProfile
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.email_log import EmailLog
from app.services.template_renderer import TemplateRenderer
from app.core.security import decrypt_secret

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, db: Session, max_retries: int = 3):
        self.db = db
        self.max_retries = max_retries
        self._smtp_client: Optional[aiosmtplib.SMTP] = None
        self._active_profile: Optional[SMTPProfile] = None
    
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def get_active_smtp_profile(self) -> Optional[SMTPProfile]:
        """Get active SMTP profile"""
        return self.db.query(SMTPProfile).filter(
            SMTPProfile.is_active == True
        ).first()

    async def connect(self):
        """Establish and reuse SMTP connection based on the active profile."""
        profile = await self.get_active_smtp_profile()
        if not profile:
            raise Exception("No active SMTP profile found")
        
        self._active_profile = profile

        use_tls = profile.tls_enabled and profile.smtp_port == 465
        start_tls = profile.tls_enabled and not use_tls

        self._smtp_client = aiosmtplib.SMTP(
            hostname=profile.smtp_host,
            port=profile.smtp_port,
            use_tls=use_tls,
            start_tls=start_tls,
            timeout=30.0
        )
        
        await self._smtp_client.connect()
        password = decrypt_secret(profile.password)
        await self._smtp_client.login(profile.username, password)
        logger.info(f"Connected to SMTP server at {profile.smtp_host}:{profile.smtp_port}")

    async def disconnect(self):
        """Close the SMTP connection safely."""
        if self._smtp_client and self._smtp_client.is_connected:
            await self._smtp_client.quit()
            self._smtp_client = None
            logger.info("Disconnected from SMTP server.")

    async def _ensure_connected(self):
        """Ensure connection is alive, reconnect if necessary."""
        if not self._smtp_client or not self._smtp_client.is_connected:
            logger.info("SMTP Connection lost. Reconnecting...")
            await self.connect()
            
    def personalize_content(self, template: str, contact: Contact) -> str:
        """Replace personalization tags"""
        variables = {
            "first_name": contact.first_name or "",
            "last_name": contact.last_name or "",
            "email": contact.email or "",
            "phone": getattr(contact, "phone", "") or "",
            "company": getattr(contact, "company", "") or "",
        }
        return TemplateRenderer.render(template, variables)

    async def send_raw_email(self, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None, tracking_id: str = None) -> bool:
        """
        Send an email with plain text fallback, proper MIME formatting, and retry logic.
        """
        await self._ensure_connected()

        # Create message with alternative subtype for HTML/Plain fallback
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{self._active_profile.sender_name} <{self._active_profile.sender_email}>"
        message["To"] = to_email
        message["Reply-To"] = self._active_profile.sender_email
        message["Message-ID"] = f"<{tracking_id or uuid.uuid4()}@carlyshayn.com>"
        message["Date"] = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
        message["MIME-Version"] = "1.0"

        # Attach parts - plain text must come before HTML in 'alternative' subtype
        if text_body:
            message.attach(MIMEText(text_body, "plain"))
        else:
            message.attach(MIMEText("Please enable HTML to view this email.", "plain"))

        message.attach(MIMEText(html_body, "html"))

        # Retry logic
        for attempt in range(self.max_retries):
            try:
                await self._ensure_connected()
                await self._smtp_client.send_message(message)
                return True
            except (aiosmtplib.SMTPException, OSError) as e:
                logger.warning(f"Email sending failed to {to_email} (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to send email to {to_email} after {self.max_retries} attempts.")
                    raise e
        return False

    async def send_email(self, contact: Contact, campaign: Campaign) -> EmailLog:
        """Send a single email for a campaign and create a log entry."""
        tracking_id = str(uuid.uuid4())
        
        # Personalize content
        subject = self.personalize_content(campaign.subject, contact)
        
        # Use campaign.template field
        raw_content = self.personalize_content(campaign.template, contact)
        
        # Convert plain text newlines to HTML line breaks
        html_content = raw_content.replace('\n', '<br>')

        # Add unsubscribe link and tracking pixel
        unsubscribe_link = f"http://localhost:8000/api/v1/unsubscribe/{tracking_id}"
        tracking_pixel = f"http://localhost:8000/api/v1/tracking/open/{tracking_id}"
        
        tracked_html = (
            f"<div style='font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #333;'>"
            f"{html_content}"
            f"</div>"
            f"<br><br>"
            f"<div style='font-size: 12px; color: #666; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;'>"
            f"<a href='{unsubscribe_link}' style='color: #666; text-decoration: underline;'>Unsubscribe</a> | "
            f"This email was sent to {contact.email}"
            f"</div>"
            f"<img src='{tracking_pixel}' width='1' height='1' style='display:none;' />"
        )
        
        # Simple plain text fallback
        text_content = (
            raw_content
            + f"\n\n---\nUnsubscribe: {unsubscribe_link}\nThis email was sent to {contact.email}"
        )

        log = EmailLog(
            campaign_id=campaign.id,
            contact_id=contact.id,
            recipient_email=contact.email,
            subject=subject,
            body=tracked_html,
            tracking_id=tracking_id,
            delivery_status="pending"
        )
        
        try:
            success = await self.send_raw_email(
                to_email=contact.email,
                subject=subject,
                html_body=tracked_html,
                text_body=text_content,
                tracking_id=tracking_id
            )
            
            if success:
                log.delivery_status = "delivered"
                log.sent_at = datetime.now(timezone.utc)
                log.delivered_at = datetime.now(timezone.utc)
                campaign.sent_count += 1
                campaign.delivered_count += 1
        
        except Exception as e:
            log.delivery_status = "failed"
            log.error_message = str(e)
            campaign.failed_count += 1
        
        self.db.add(log)
        self.db.commit()
        return log
    
    async def send_campaign(self, campaign_id: int):
        """Send all emails for a campaign leveraging connection reuse."""
        campaign = self.db.query(Campaign).filter(
            Campaign.id == campaign_id
        ).first()
        
        if not campaign:
            return
            
        # Get all recipients/contacts
        contacts = self.db.query(Contact).filter(
            Contact.campaign_id == campaign_id
        ).all()
        
        # Use context manager for connection reuse across all emails
        async with self:
            for contact in contacts:
                await self.send_email(contact, campaign)
