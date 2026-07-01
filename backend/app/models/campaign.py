"""
Campaign database model
Stores email campaign information and statistics
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Enum,
    Index, CheckConstraint, ForeignKey
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
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Owner
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    campaign_name = Column(String(200), index=True, nullable=False)
    subject = Column(String(500), nullable=False)
    template = Column(Text, nullable=False)
    
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False, index=True)
    
    total_emails = Column(Integer, default=0, nullable=False)
    sent_count = Column(Integer, default=0, nullable=False)
    delivered_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    opened_count = Column(Integer, default=0, nullable=False)
    bounced_count = Column(Integer, default=0, nullable=False)
    unsubscribed_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    contacts = relationship("Contact", back_populates="campaign", cascade="all, delete-orphan", lazy="dynamic")
    email_logs = relationship("EmailLog", back_populates="campaign", cascade="all, delete-orphan", lazy="dynamic")
    
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
        Index('idx_campaign_user', 'user_id'),
    )
    
    @property
    def delivery_rate(self):
        if self.sent_count == 0:
            return 0.0
        return (self.delivered_count / self.sent_count) * 100
    
    @property
    def open_rate(self):
        if self.delivered_count == 0:
            return 0.0
        return (self.opened_count / self.delivered_count) * 100
