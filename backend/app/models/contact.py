"""
Contact database model
Stores campaign recipients/contacts with unsubscribe support
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, DateTime, Text,
    Index, UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Contact(Base):
    """
    Contact Model
    Stores recipient information for campaigns with unsubscribe tracking
    """
    __tablename__ = "contacts"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key
    campaign_id = Column(
        Integer, 
        ForeignKey("campaigns.id", ondelete="CASCADE"), 
        nullable=False,
        index=True,
        comment="Reference to parent campaign"
    )
    
    # Contact Information
    first_name = Column(
        String(100), 
        nullable=False,
        comment="Recipient first name for personalization"
    )
    last_name = Column(
        String(100), 
        nullable=False,
        comment="Recipient last name for personalization"
    )
    email = Column(
        String(255), 
        nullable=False,
        index=True,
        comment="Recipient email address"
    )
    
    # Additional Fields (Optional)
    phone = Column(
        String(20),
        nullable=True,
        comment="Optional phone number"
    )
    company = Column(
        String(200),
        nullable=True,
        comment="Optional company name"
    )
    
    # Unsubscribe Management
    unsubscribed = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether contact has unsubscribed"
    )
    unsubscribed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Unsubscribe timestamp"
    )
    unsubscribe_token = Column(
        String(64),
        unique=True,
        index=True,
        nullable=True,
        comment="Unique unsubscribe token for this contact"
    )
    unsubscribe_reason = Column(
        Text,
        nullable=True,
        comment="Reason for unsubscribing (if provided)"
    )
    unsubscribe_ip = Column(
        String(45),
        nullable=True,
        comment="IP address from which unsubscribe was requested"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        comment="Contact creation timestamp"
    )
    uploaded_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        comment="CSV upload timestamp"
    )
    
    # Relationships
    campaign = relationship(
        "Campaign", 
        back_populates="contacts"
    )
    email_logs = relationship(
        "EmailLog", 
        back_populates="contact",
        cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('campaign_id', 'email', name='unique_contact_per_campaign'),
        Index('idx_contact_campaign', 'campaign_id'),
        Index('idx_contact_email', 'email'),
        Index('idx_contact_name', 'first_name', 'last_name'),
        Index('idx_contact_unsubscribed', 'unsubscribed'),
        Index('idx_contact_unsub_token', 'unsubscribe_token'),
        Index('idx_contact_unsub_at', 'unsubscribed_at'),
        {'comment': 'Campaign recipients with personalization data and unsubscribe tracking'}
    )
    
    # Properties
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_subscribed(self) -> bool:
        """Check if contact is still subscribed"""
        return not self.unsubscribed
    
    def __repr__(self):
        return f"<Contact(id={self.id}, email='{self.email}', campaign_id={self.campaign_id}, unsubscribed={self.unsubscribed})>"
