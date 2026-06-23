"""
Export service for email analytics data
Handles CSV and Excel exports with comprehensive filtering
"""
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from datetime import datetime
from typing import Optional, List, Dict
import pandas as pd
import io
import logging

from app.models.email_log import EmailLog
from app.models.contact import Contact
from app.models.campaign import Campaign

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting email analytics data"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==========================================================================
    # MAIN EXPORT FUNCTION
    # ==========================================================================
    
    async def export_emails(
        self,
        status: str,
        format: str = "csv",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        campaign_id: Optional[int] = None
    ) -> StreamingResponse:
        """
        Export emails based on status with filtering
        
        Args:
            status: Email status ('delivered', 'opened', 'bounced', 'unsubscribed', 'all')
            format: Export format ('csv' or 'xlsx')
            start_date: Optional start date filter
            end_date: Optional end date filter
            campaign_id: Optional campaign filter
            
        Returns:
            StreamingResponse with file download
        """
        logger.info(
            f"Exporting {status} emails: format={format}, "
            f"campaign_id={campaign_id}, date_range={start_date} to {end_date}"
        )
        
        # Build query
        query = self.db.query(EmailLog).join(Contact)
        
        # Apply filters
        if campaign_id:
            query = query.filter(EmailLog.campaign_id == campaign_id)
        
        if start_date:
            query = query.filter(EmailLog.sent_at >= start_date)
        
        if end_date:
            query = query.filter(EmailLog.sent_at <= end_date)
        
        # Filter by status
        if status == "delivered":
            query = query.filter(EmailLog.delivery_status == 'delivered')
        elif status == "opened":
            query = query.filter(EmailLog.opened == True)
        elif status == "bounced":
            query = query.filter(EmailLog.bounced == True)
        elif status == "unsubscribed":
            query = query.filter(EmailLog.unsubscribed == True)
        elif status == "failed":
            query = query.filter(EmailLog.delivery_status == 'failed')
        # 'all' status exports everything
        
        # Get data with joins
        logs = query.all()
        
        logger.info(f"Retrieved {len(logs)} records for export")
        
        # Convert to DataFrame
        data = self._prepare_export_data(logs, status)
        df = pd.DataFrame(data)
        
        # Generate file
        output = io.BytesIO()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == "csv":
            df.to_csv(output, index=False, encoding='utf-8-sig')  # UTF-8 with BOM for Excel
            media_type = "text/csv"
            filename = f"email_export_{status}_{timestamp}.csv"
        else:  # xlsx
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Email Export')
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Email Export']
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"email_export_{status}_{timestamp}.xlsx"
        
        output.seek(0)
        
        logger.info(f"Export complete: {filename}")
        
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": media_type
            }
        )
    
    def _prepare_export_data(self, logs: List[EmailLog], status: str) -> List[Dict]:
        """
        Prepare email log data for export
        
        Args:
            logs: List of EmailLog objects
            status: Export status type
            
        Returns:
            List of dictionaries ready for DataFrame
        """
        data = []
        
        for log in logs:
            row = {
                "Email": log.recipient_email,
                "First Name": log.contact.first_name if log.contact else "",
                "Last Name": log.contact.last_name if log.contact else "",
                "Campaign ID": log.campaign_id,
                "Subject": log.subject,
                "Sent At": log.sent_at.strftime('%Y-%m-%d %H:%M:%S') if log.sent_at else "",
                "Delivery Status": log.delivery_status,
            }
            
            # Add status-specific columns
            if status in ["delivered", "all"]:
                row["Delivered At"] = log.delivered_at.strftime('%Y-%m-%d %H:%M:%S') if log.delivered_at else ""
            
            if status in ["opened", "all"]:
                row["Opened"] = "Yes" if log.opened else "No"
                row["Opened At"] = log.opened_at.strftime('%Y-%m-%d %H:%M:%S') if log.opened_at else ""
                row["Open Count"] = log.open_count or 0
            
            if status in ["bounced", "all"]:
                row["Bounced"] = "Yes" if log.bounced else "No"
                row["Bounce Type"] = log.bounce_type or ""
                row["Bounce Reason"] = log.error_message[:200] if log.error_message else ""
                row["Bounced At"] = log.bounced_at.strftime('%Y-%m-%d %H:%M:%S') if log.bounced_at else ""
            
            if status in ["unsubscribed", "all"]:
                row["Unsubscribed"] = "Yes" if log.unsubscribed else "No"
                row["Unsubscribed At"] = log.unsubscribed_at.strftime('%Y-%m-%d %H:%M:%S') if log.unsubscribed_at else ""
            
            if status == "all":
                row["Tracking ID"] = log.tracking_id or ""
                row["IP Address"] = log.ip_address or ""
            
            data.append(row)
        
        return data
    
    # ==========================================================================
    # SPECIFIC EXPORT METHODS
    # ==========================================================================
    
    async def export_delivered(
        self,
        format: str = "csv",
        campaign_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> StreamingResponse:
        """Export delivered emails"""
        return await self.export_emails(
            status="delivered",
            format=format,
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
    
    async def export_opened(
        self,
        format: str = "csv",
        campaign_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> StreamingResponse:
        """Export opened emails"""
        return await self.export_emails(
            status="opened",
            format=format,
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
    
    async def export_bounced(
        self,
        format: str = "csv",
        campaign_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> StreamingResponse:
        """Export bounced emails"""
        return await self.export_emails(
            status="bounced",
            format=format,
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
    
    async def export_unsubscribed(
        self,
        format: str = "csv",
        campaign_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> StreamingResponse:
        """Export unsubscribed emails"""
        return await self.export_emails(
            status="unsubscribed",
            format=format,
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
    
    async def export_all(
        self,
        format: str = "csv",
        campaign_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> StreamingResponse:
        """Export all emails with complete data"""
        return await self.export_emails(
            status="all",
            format=format,
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
    
    # ==========================================================================
    # CAMPAIGN SUMMARY EXPORT
    # ==========================================================================
    
    async def export_campaign_summary(
        self,
        campaign_id: int,
        format: str = "xlsx"
    ) -> StreamingResponse:
        """
        Export comprehensive campaign summary report
        
        Args:
            campaign_id: Campaign ID
            format: Export format ('csv' or 'xlsx')
            
        Returns:
            StreamingResponse with report
        """
        # Get campaign
        campaign = self.db.query(Campaign).filter(
            Campaign.id == campaign_id
        ).first()
        
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Get all email logs for campaign
        logs = self.db.query(EmailLog).filter(
            EmailLog.campaign_id == campaign_id
        ).all()
        
        # Prepare summary data
        summary_data = {
            "Campaign Name": [campaign.campaign_name],
            "Total Emails": [campaign.total_emails],
            "Sent": [campaign.sent_count],
            "Delivered": [campaign.delivered_count],
            "Opened": [campaign.opened_count],
            "Bounced": [campaign.bounced_count],
            "Unsubscribed": [campaign.unsubscribed_count],
            "Delivery Rate": [f"{campaign.delivery_rate:.2f}%"],
            "Open Rate": [f"{campaign.open_rate:.2f}%"],
            "Bounce Rate": [f"{campaign.bounce_rate:.2f}%"],
            "Status": [campaign.status.value],
            "Created At": [campaign.created_at.strftime('%Y-%m-%d %H:%M:%S')],
        }
        
        summary_df = pd.DataFrame(summary_data)
        
        # Prepare detailed email data
        email_data = self._prepare_export_data(logs, "all")
        email_df = pd.DataFrame(email_data)
        
        # Generate file
        output = io.BytesIO()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == "xlsx":
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Summary sheet
                summary_df.to_excel(writer, index=False, sheet_name='Summary')
                
                # Detailed data sheet
                email_df.to_excel(writer, index=False, sheet_name='Email Details')
                
                # Auto-adjust widths
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for idx, col in enumerate(writer.sheets[sheet_name].columns):
                        max_length = 15  # Default width
                        worksheet.column_dimensions[chr(65 + idx)].width = max_length
            
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"campaign_{campaign_id}_report_{timestamp}.xlsx"
        else:
            # CSV only exports detailed data
            email_df.to_csv(output, index=False, encoding='utf-8-sig')
            media_type = "text/csv"
            filename = f"campaign_{campaign_id}_report_{timestamp}.csv"
        
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": media_type
            }
        )
    
    # ==========================================================================
    # UTILITY METHODS
    # ==========================================================================
    
    def get_export_preview(
        self,
        status: str,
        campaign_id: Optional[int] = None,
        limit: int = 10
    ) -> Dict:
        """
        Get preview of export data
        
        Args:
            status: Email status
            campaign_id: Optional campaign filter
            limit: Number of preview rows
            
        Returns:
            Dictionary with preview data and count
        """
        query = self.db.query(EmailLog)
        
        if campaign_id:
            query = query.filter(EmailLog.campaign_id == campaign_id)
        
        # Filter by status
        if status == "delivered":
            query = query.filter(EmailLog.delivery_status == 'delivered')
        elif status == "opened":
            query = query.filter(EmailLog.opened == True)
        elif status == "bounced":
            query = query.filter(EmailLog.bounced == True)
        elif status == "unsubscribed":
            query = query.filter(EmailLog.unsubscribed == True)
        
        total_count = query.count()
        preview_logs = query.limit(limit).all()
        
        preview_data = self._prepare_export_data(preview_logs, status)
        
        return {
            "total_count": total_count,
            "preview_count": len(preview_data),
            "preview_data": preview_data[:limit],
            "status": status,
            "campaign_id": campaign_id
        }
