"""
Base class for all database models
Import all models for Alembic migrations
"""
from sqlalchemy.ext.declarative import declarative_base

# Create declarative base
Base = declarative_base()

# Import all models here for Alembic to detect them
from app.models.smtp_profile import SMTPProfile
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.email_log import EmailLog
from app.models.template import Template

# Ensure all models are registered
__all__ = [
    "Base",
    "SMTPProfile",
    "Campaign",
    "Contact",
    "EmailLog",
    "Template"
]
