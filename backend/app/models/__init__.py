"""
Database models package
"""
from app.models.smtp_profile import SMTPProfile
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.email_log import EmailLog
from app.models.user import User
from app.models.template import Template
from app.models.notification import Notification

__all__ = [
    "SMTPProfile", "Campaign", "Contact",
    "EmailLog", "User", "Template", "Notification"
]
