"""
Campaign database model
Stores email campaign information and statistics
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Enum,
    Index, CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class CampaignStatus(str, enum.Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class Campaign(Base):
    """
    Campaign Model
    Manages email marketing campaigns with tracking statistics
    """
    __tablename__ = "campaigns"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Campaign Details
    campaign_name = Column(
        String(200), 
        index=True, 
        nullable=False,
        comment="Campaign display name"
    )
    subject = Column(
        String(500), 
        nullable=False,
        comment="Email subject line (supports {{variables}})"
    )
    template = Column(
        Text, 
        nullable=False,
        comment="Email body template (supports {{first_name}}, {{last_name}}, {{email}})"
    )
    
    # Status
    status = Column(
        Enum(CampaignStatus), 
        default=CampaignStatus.DRAFT,
        nullable=False,
        index=True,
        comment="Current campaign status"
    )
    
    # Statistics - Total
    total_emails = Column(
        Integer, 
        default=0, 
        nullable=False,
        comment="Total number of recipients"
    )
    
    # Statistics - Sending
    sent_count = Column(
        Integer, 
        default=0, 
        nullable=False,
        comment="Number of emails sent"
    )
    delivered_count = Column(
        Integer, 
        default=0, 
        nullable=False,
        comment="Number of emails delivered successfully"
    )
    failed_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of emails that failed to send"
    )
    
    # Statistics - Engagement
    opened_count = Column(
        Integer, 
        default=0, 
        nullable=False,
        comment="Number of emails opened by recipients"
    )
    
    # Statistics - Issues
    bounced_count = Column(
        Integer, 
        default=0, 
        nullable=False,
        comment="Number of bounced emails"
    )
    unsubscribed_count = Column(
        Integer, 
        default=0, 
        nullable=False,
        comment="Number of unsubscribed recipients"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        index=True,
        comment="Campaign creation timestamp"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        onupdate=func.now(),
        comment="Last update timestamp"
    )
    scheduled_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Scheduled send time"
    )
    started_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Campaign start timestamp"
    )
    completed_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Campaign completion timestamp"
    )
    
    # Relationships
    contacts = relationship(
        "Contact", 
        back_populates="campaign",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    email_logs = relationship(
        "EmailLog", 
        back_populates="campaign",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint('total_emails >= 0', name='valid_total_emails'),
        CheckConstraint('sent_count >= 0', name='valid_sent_count'),
        CheckConstraint('delivered_count >= 0', name='valid_delivered_count'),
        CheckConstraint('failed_count >= 0', name='valid_failed_count'),
        CheckConstraint('opened_count >= 0', name='valid_opened_count'),
        CheckConstraint('bounced_count >= 0', name='valid_bounced_count'),
        CheckConstraint('unsubscribed_count >= 0', name='valid_unsubscribed_count'),
        Index('idx_campaign_status', 'status'),
        Index('idx_campaign_created', 'created_at'),
        Index('idx_campaign_name', 'campaign_name'),
        {'comment': 'Email marketing campaigns with statistics'}
    )
    
    # Properties
    @property
    def delivery_rate(self) -> float:
        """Calculate delivery rate percentage"""
        if self.sent_count == 0:
            return 0.0
        return (self.delivered_count / self.sent_count) * 100
    
    @property
    def open_rate(self) -> float:
        """Calculate open rate percentage"""
        if self.delivered_count == 0:
            return 0.0
        return (self.opened_count / self.delivered_count) * 100
    
    @property
    def bounce_rate(self) -> float:
        """Calculate bounce rate percentage"""
        if self.sent_count == 0:
            return 0.0
        return (self.bounced_count / self.sent_count) * 100
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.campaign_name}', status='{self.status.value}')>"
