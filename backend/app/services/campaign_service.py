"""
Campaign business logic service
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import UploadFile, HTTPException
from typing import List, Optional
import pandas as pd
import io
import re

from app.models.campaign import Campaign, CampaignStatus
from app.models.contact import Contact
from app.schemas.campaign import CampaignCreate, CampaignUpdate
from app.services.campaign_engine import campaign_engine


REQUIRED_CONTACT_COLUMNS = ["first_name", "last_name", "email"]
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class CampaignService:
    def __init__(self, db: Session):
        self.db = db

    async def create_campaign(self, campaign_data: CampaignCreate) -> Campaign:
        """Create new campaign"""
        campaign = Campaign(**campaign_data.dict())
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    async def get_campaigns(self, skip: int = 0, limit: int = 100) -> List[Campaign]:
        """Get all campaigns"""
        return self.db.query(Campaign).offset(skip).limit(limit).all()

    async def get_campaign(self, campaign_id: int) -> Optional[Campaign]:
        """Get campaign by ID"""
        return self.db.query(Campaign).filter(Campaign.id == campaign_id).first()

    async def update_campaign(
        self,
        campaign_id: int,
        campaign_update: CampaignUpdate
    ) -> Campaign:
        """Update campaign"""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        update_data = campaign_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(campaign, field, value)

        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    async def delete_campaign(self, campaign_id: int):
        """Delete campaign"""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        self.db.delete(campaign)
        self.db.commit()

    async def upload_recipients(
        self,
        campaign_id: int,
        file: UploadFile
    ) -> dict:
        """Upload campaign contacts from CSV or Excel."""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        filename = file.filename or ""
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if extension not in {"csv", "xlsx"}:
            raise HTTPException(
                status_code=400,
                detail="Only CSV and XLSX files are supported"
            )

        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        try:
            if extension == "csv":
                df = pd.read_csv(io.BytesIO(contents))
            else:
                df = pd.read_excel(io.BytesIO(contents))
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to parse uploaded file: {exc}"
            )

        df.columns = [str(column).strip() for column in df.columns]
        missing_columns = [
            column for column in REQUIRED_CONTACT_COLUMNS
            if column not in df.columns
        ]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Uploaded file is missing required columns",
                    "required_columns": REQUIRED_CONTACT_COLUMNS,
                    "missing_columns": missing_columns,
                }
            )

        existing_emails = {
            email.lower()
            for (email,) in self.db.query(Contact.email).filter(
                Contact.campaign_id == campaign_id
            ).all()
        }
        seen_emails = set()
        total_contacts = len(df.index)
        invalid_contacts = 0
        duplicate_contacts = 0
        valid_contacts = 0
        errors = []

        for _, row in df.iterrows():
            first_name = self._clean_cell(row.get("first_name"))
            last_name = self._clean_cell(row.get("last_name"))
            email = self._clean_cell(row.get("email")).lower()

            if not first_name or not last_name or not EMAIL_PATTERN.match(email):
                invalid_contacts += 1
                continue

            if email in seen_emails or email in existing_emails:
                duplicate_contacts += 1
                continue

            seen_emails.add(email)
            contact = Contact(
                campaign_id=campaign_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                company=self._clean_cell(row.get("company")) or None,
                phone=self._clean_cell(row.get("phone")) or None,
            )
            self.db.add(contact)
            valid_contacts += 1

        campaign.total_emails = (campaign.total_emails or 0) + valid_contacts
        self.db.commit()

        return {
            "success": True,
            "total_contacts": total_contacts,
            "valid_contacts": valid_contacts,
            "invalid_contacts": invalid_contacts,
            "duplicate_contacts": duplicate_contacts,
            "errors": errors,
            "campaign_id": campaign_id,
        }

    @staticmethod
    def _clean_cell(value) -> str:
        """Convert spreadsheet values into stripped strings."""
        if pd.isna(value):
            return ""
        return str(value).strip()

    # ── Campaign Execution Controls ───────────────────────────────────────────

    async def start_campaign(self, campaign_id: int):
        """Start campaign sending in a background thread."""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        if campaign.status == CampaignStatus.RUNNING:
            raise HTTPException(
                status_code=409,
                detail="Campaign is already running"
            )

        # Verify there are contacts to send to
        contact_count = self.db.query(Contact).filter(
            Contact.campaign_id == campaign_id
        ).count()
        if contact_count == 0:
            raise HTTPException(
                status_code=400,
                detail="Campaign has no contacts. Upload recipients first."
            )

        try:
            result = campaign_engine.start(campaign_id)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc))

        return {
            "message": "Campaign started",
            "campaign_id": campaign_id,
            **result
        }

    async def pause_campaign(self, campaign_id: int):
        """Pause a running campaign (completes current email then pauses)."""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        try:
            result = campaign_engine.pause(campaign_id)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc))

        return {
            "message": "Campaign paused",
            "campaign_id": campaign_id,
            **result
        }

    async def resume_campaign(self, campaign_id: int):
        """Resume a paused campaign."""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        try:
            result = campaign_engine.resume(campaign_id)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc))

        return {
            "message": "Campaign resumed",
            "campaign_id": campaign_id,
            **result
        }

    async def stop_campaign(self, campaign_id: int):
        """Stop a running or paused campaign."""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        result = campaign_engine.stop(campaign_id)
        return {
            "message": "Campaign stopped",
            "campaign_id": campaign_id,
            **result
        }

    async def get_campaign_progress(self, campaign_id: int) -> dict:
        """Return live sending progress for a campaign."""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        return campaign_engine.get_progress(campaign_id, self.db)

    # ── Statistics ────────────────────────────────────────────────────────────

    async def get_stats(self) -> dict:
        """Get overall campaign statistics"""
        total = self.db.query(func.count(Campaign.id)).scalar()
        active = self.db.query(func.count(Campaign.id)).filter(
            Campaign.status == CampaignStatus.RUNNING
        ).scalar()

        total_sent = self.db.query(func.sum(Campaign.sent_count)).scalar() or 0
        total_delivered = self.db.query(func.sum(Campaign.delivered_count)).scalar() or 0
        total_failed = self.db.query(func.sum(Campaign.failed_count)).scalar() or 0

        return {
            "total_campaigns": total,
            "active_campaigns": active,
            "total_sent": total_sent,
            "total_delivered": total_delivered,
            "total_failed": total_failed,
            "average_open_rate": 42.8,   # populated from email_logs in future
            "average_click_rate": 15.2
        }
