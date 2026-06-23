"""
Recipient business logic service
"""
from sqlalchemy.orm import Session
from typing import List

from app.models.contact import Contact


class RecipientService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_recipients_by_campaign(
        self, 
        campaign_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Contact]:
        """Get all recipients for a campaign"""
        return self.db.query(Contact).filter(
            Contact.campaign_id == campaign_id
        ).offset(skip).limit(limit).all()
