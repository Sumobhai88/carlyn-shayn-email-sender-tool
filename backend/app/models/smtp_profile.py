"""
SMTP Profile database model
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    Index, CheckConstraint, Text, ForeignKey
)
from sqlalchemy.sql import func
from app.db.base import Base


class SMTPProfile(Base):
    __tablename__ = "smtp_profiles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Owner
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    profile_name = Column(String(100), index=True, nullable=False)
    sender_name = Column(String(200), nullable=False)
    sender_email = Column(String(255), nullable=False, index=True)
    smtp_host = Column(String(255), nullable=False)
    smtp_port = Column(Integer, nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(Text, nullable=False)
    tls_enabled = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False, index=True)
    status = Column(String(20), default="connected")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint('smtp_port > 0 AND smtp_port <= 65535', name='valid_port'),
        CheckConstraint("status IN ('connected', 'failed', 'testing')", name='valid_status'),
        Index('idx_smtp_active', 'is_active'),
        Index('idx_smtp_email', 'sender_email'),
        Index('idx_smtp_user', 'user_id'),
        # profile_name is unique per user, not globally
    )
