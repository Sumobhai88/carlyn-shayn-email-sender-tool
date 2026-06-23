"""
SMTP Profile database model
Stores email server configurations for sending emails
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    Index, CheckConstraint, Text
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class SMTPProfile(Base):
    """
    SMTP Profile Model
    Manages email server configurations (Gmail, Zoho, Custom SMTP)
    
    Note: Password is stored as an encoded secret and excluded from API responses.
    For SMTP connections, the service decodes it before use.
    """
    __tablename__ = "smtp_profiles"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Profile Information
    profile_name = Column(
        String(100), 
        unique=True, 
        index=True, 
        nullable=False,
        comment="Unique name for the SMTP profile"
    )
    
    # Sender Details
    sender_name = Column(
        String(200), 
        nullable=False,
        comment="Display name for sent emails"
    )
    sender_email = Column(
        String(255), 
        nullable=False, 
        index=True,
        comment="Email address for From field"
    )
    
    # SMTP Server Configuration
    smtp_host = Column(
        String(255), 
        nullable=False,
        comment="SMTP server hostname (e.g., smtp.gmail.com)"
    )
    smtp_port = Column(
        Integer, 
        nullable=False,
        comment="SMTP server port (usually 587 or 465)"
    )
    
    # Authentication
    username = Column(
        String(255), 
        nullable=False,
        comment="SMTP authentication username"
    )
    password = Column(
        Text, 
        nullable=False,
        comment="Encoded SMTP password"
    )
    
    # Settings
    tls_enabled = Column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Enable TLS/SSL encryption"
    )
    is_active = Column(
        Boolean, 
        default=False, 
        nullable=False, 
        index=True,
        comment="Currently active profile (only one can be active)"
    )
    
    # Status
    status = Column(
        String(20), 
        default="connected",
        comment="Connection status: connected, failed, testing"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        comment="Profile creation timestamp"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        onupdate=func.now(),
        comment="Last update timestamp"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint('smtp_port > 0 AND smtp_port <= 65535', name='valid_port'),
        CheckConstraint("status IN ('connected', 'failed', 'testing')", name='valid_status'),
        Index('idx_smtp_active', 'is_active'),
        Index('idx_smtp_email', 'sender_email'),
        {'comment': 'SMTP server profiles for email sending'}
    )
    
    def __repr__(self):
        return f"<SMTPProfile(id={self.id}, name='{self.profile_name}', active={self.is_active})>"
