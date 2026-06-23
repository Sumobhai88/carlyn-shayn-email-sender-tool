"""
Email Log database model for tracking
Comprehensive email delivery and engagement tracking
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, DateTime, Text,
    Index, CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class EmailLog(Base):
    """
    Email Log Model
    Tracks every email sent with detailed delivery and engagement metrics
    """
    __tablename__ = "email_logs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys
    campaign_id = Column(
        Integer, 
        ForeignKey("campaigns.id", ondelete="CASCADE"), 
        nullable=False,
        index=True,
        comment="Reference to parent campaign"
    )
    contact_id = Column(
        Integer, 
        ForeignKey("contacts.id", ondelete="CASCADE"), 
        nullable=False,
        index=True,
        comment="Reference to recipient contact"
    )
    
    # Email Details
    recipient_email = Column(
        String(255), 
        nullable=False,
        index=True,
        comment="Recipient email address"
    )
    subject = Column(
        String(500), 
        nullable=False,
        comment="Email subject (personalized)"
    )
    body = Column(
        Text, 
        nullable=False,
        comment="Email body content (personalized)"
    )
    
    # Delivery Status
    delivery_status = Column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
        comment="Delivery status: pending, sent, delivered, failed, bounced"
    )
    
    # Tracking Flags
    opened = Column(
        Boolean, 
        default=False,
        nullable=False,
        index=True,
        comment="Email was opened by recipient"
    )
    bounced = Column(
        Boolean, 
        default=False,
        nullable=False,
        index=True,
        comment="Email bounced back"
    )
    unsubscribed = Column(
        Boolean, 
        default=False,
        nullable=False,
        index=True,
        comment="Recipient unsubscribed"
    )
    
    # Error Information
    error_message = Column(
        Text, 
        nullable=True,
        comment="Error details if sending failed"
    )
    bounce_type = Column(
        String(20),
        nullable=True,
        comment="Bounce type: hard, soft, complaint"
    )
    
    # Tracking Details
    tracking_id = Column(
        String(100), 
        unique=True,
        index=True,
        comment="Unique tracking identifier (UUID)"
    )
    ip_address = Column(
        String(45), 
        nullable=True,
        comment="IP address when email was opened"
    )
    user_agent = Column(
        String(500), 
        nullable=True,
        comment="Browser/client user agent"
    )
    
    # Timestamps - Sending
    sent_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        index=True,
        comment="Email sent timestamp"
    )
    delivered_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Email delivered timestamp"
    )
    
    # Timestamps - Engagement
    opened_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        index=True,
        comment="First email open timestamp"
    )
    last_opened_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Most recent open timestamp"
    )
    open_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times opened"
    )
    
    # Timestamps - Issues
    bounced_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Email bounce timestamp"
    )
    unsubscribed_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Unsubscribe timestamp"
    )
    
    # Metadata
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False,
        comment="Log entry creation timestamp"
    )
    
    # Relationships
    campaign = relationship(
        "Campaign", 
        back_populates="email_logs"
    )
    contact = relationship(
        "Contact", 
        back_populates="email_logs"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "delivery_status IN ('pending', 'sent', 'delivered', 'failed', 'bounced')", 
            name='valid_delivery_status'
        ),
        CheckConstraint(
            "bounce_type IS NULL OR bounce_type IN ('hard', 'soft', 'complaint')", 
            name='valid_bounce_type'
        ),
        CheckConstraint('open_count >= 0', name='valid_open_count'),
        Index('idx_email_log_campaign', 'campaign_id'),
        Index('idx_email_log_contact', 'contact_id'),
        Index('idx_email_log_email', 'recipient_email'),
        Index('idx_email_log_delivery', 'delivery_status'),
        Index('idx_email_log_opened', 'opened'),
        Index('idx_email_log_tracking', 'tracking_id'),
        Index('idx_email_log_sent', 'sent_at'),
        Index('idx_email_log_opened_at', 'opened_at'),
        # Composite indexes for common queries
        Index('idx_campaign_delivery', 'campaign_id', 'delivery_status'),
        Index('idx_campaign_opened', 'campaign_id', 'opened'),
        Index('idx_campaign_bounced', 'campaign_id', 'bounced'),
        {'comment': 'Comprehensive email tracking and analytics'}
    )
    
    # Properties
    @property
    def is_delivered(self) -> bool:
        """Check if email was delivered"""
        return self.delivery_status == 'delivered'
    
    @property
    def is_failed(self) -> bool:
        """Check if email failed"""
        return self.delivery_status == 'failed'
    
    @property
    def is_pending(self) -> bool:
        """Check if email is pending"""
        return self.delivery_status == 'pending'
    
    def __repr__(self):
        return f"<EmailLog(id={self.id}, email='{self.recipient_email}', status='{self.delivery_status}')>"

