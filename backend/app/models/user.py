"""
User model for authentication
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    google_id = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Profile settings
    company_name = Column(String, nullable=True)
    
    # Notification preferences
    notif_email = Column(Boolean, default=True)
    notif_campaigns = Column(Boolean, default=True)
    
    # Usage limits & admin controls
    email_limit = Column(Integer, default=1000)   # max emails this user can send
    emails_used = Column(Integer, default=0)      # emails sent so far
    is_blocked = Column(Boolean, default=False)   # admin can block service
