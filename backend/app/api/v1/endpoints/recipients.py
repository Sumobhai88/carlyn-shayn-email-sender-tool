"""
Recipient endpoints
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.recipient import RecipientResponse
from app.services.recipient_service import RecipientService

router = APIRouter()


@router.get("/campaign/{campaign_id}", response_model=List[RecipientResponse])
async def get_campaign_recipients(
    campaign_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all recipients for a campaign"""
    service = RecipientService(db)
    return await service.get_recipients_by_campaign(campaign_id, skip=skip, limit=limit)


@router.post("/{campaign_id}/manual")
async def add_manual_recipients(
    campaign_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Add recipients manually (comma or newline separated emails)"""
    from app.models.campaign import Campaign
    from app.models.contact import Contact
    import re
    
    emails_str = data.get('emails', '')
    
    # Split by comma or newline
    email_list = re.split(r'[,\n]+', emails_str)
    email_list = [e.strip() for e in email_list if e.strip()]
    
    # Validate emails
    email_pattern = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    valid_emails = [e for e in email_list if email_pattern.match(e)]
    
    # Get campaign
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get existing emails
    existing = {c.email for c in db.query(Contact).filter(Contact.campaign_id == campaign_id).all()}
    
    # Add new contacts
    added_count = 0
    for email in valid_emails:
        if email not in existing:
            contact = Contact(
                campaign_id=campaign_id,
                first_name=email.split('@')[0],  # Use email prefix as first name
                last_name="",
                email=email
            )
            db.add(contact)
            added_count += 1
    
    campaign.total_emails = (campaign.total_emails or 0) + added_count
    db.commit()
    
    return {
        "success": True,
        "added_count": added_count,
        "duplicate_count": len(valid_emails) - added_count,
        "invalid_count": len(email_list) - len(valid_emails)
    }

