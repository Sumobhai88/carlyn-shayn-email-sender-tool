"""
Export endpoints for email analytics data
Provides CSV and Excel exports with comprehensive filtering
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import logging

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.export_service import ExportService

router = APIRouter()
logger = logging.getLogger(__name__)


# ==============================================================================
# DELIVERED EMAILS EXPORT
# ==============================================================================

@router.get(
    "/delivered",
    summary="Export Delivered Emails",
    description="Export all delivered emails with optional filtering",
    response_class=StreamingResponse
)
async def export_delivered(
    format: str = Query("csv", regex="^(csv|xlsx)$", description="Export format: csv or xlsx"),
    campaign_id: Optional[int] = Query(None, description="Filter by campaign ID"),
    start_date: Optional[datetime] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Export delivered emails
    
    Query Parameters:
    - format: 'csv' or 'xlsx' (default: csv)
    - campaign_id: Optional campaign filter
    - start_date: Optional start date
    - end_date: Optional end date
    
    Returns:
    - File download (CSV or Excel)
    
    Columns include:
    - Email, First Name, Last Name
    - Campaign ID, Subject
    - Sent At, Delivery Status
    - Delivered At
    """
    service = ExportService(db)
    
    try:
        return await service.export_delivered(
            format=format,
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        logger.error(f"Error exporting delivered emails: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export: {str(e)}"
        )


# ==============================================================================
# OPENED EMAILS EXPORT
# ==============================================================================

@router.get(
    "/opened",
    summary="Export Opened Emails",
    description="Export all opened emails with engagement metrics",
    response_class=StreamingResponse
)
async def export_opened(
    format: str = Query("csv", regex="^(csv|xlsx)$", description="Export format"),
    campaign_id: Optional[int] = Query(None, description="Filter by campaign ID"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db)
):
    """
    Export opened emails
    
    Query Parameters:
    - format: 'csv' or 'xlsx'
    - campaign_id: Optional campaign filter
    - start_date: Optional start date
    - end_date: Optional end date
    
    Returns:
    - File download with opened emails
    
    Columns include:
    - Email, First Name, Last Name
    - Campaign ID, Subject
    - Sent At, Opened (Yes/No)
    - Opened At, Open Count
    """
    service = ExportService(db)
    
    try:
        return await service.export_opened(
            format=format,
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        logger.error(f"Error exporting opened emails: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export: {str(e)}"
        )


# ==============================================================================
# BOUNCED EMAILS EXPORT
# ==============================================================================

@router.get(
    "/bounced",
    summary="Export Bounced Emails",
    description="Export all bounced emails with bounce reasons",
    response_class=StreamingResponse
)
async def export_bounced(
    format: str = Query("csv", regex="^(csv|xlsx)$", description="Export format"),
    campaign_id: Optional[int] = Query(None, description="Filter by campaign ID"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db)
):
    """
    Export bounced emails
    
    Query Parameters:
    - format: 'csv' or 'xlsx'
    - campaign_id: Optional campaign filter
    - start_date: Optional start date
    - end_date: Optional end date
    
    Returns:
    - File download with bounced emails
    
    Columns include:
    - Email, First Name, Last Name
    - Campaign ID, Subject
    - Sent At, Bounced (Yes/No)
    - Bounce Type (hard/soft/complaint)
    - Bounce Reason
    - Bounced At
    """
    service = ExportService(db)
    
    try:
        return await service.export_bounced(
            format=format,
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        logger.error(f"Error exporting bounced emails: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export: {str(e)}"
        )


# ==============================================================================
# UNSUBSCRIBED EMAILS EXPORT
# ==============================================================================

@router.get(
    "/unsubscribed",
    summary="Export Unsubscribed Emails",
    description="Export all unsubscribed emails",
    response_class=StreamingResponse
)
async def export_unsubscribed(
    format: str = Query("csv", regex="^(csv|xlsx)$", description="Export format"),
    campaign_id: Optional[int] = Query(None, description="Filter by campaign ID"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db)
):
    """
    Export unsubscribed emails
    
    Query Parameters:
    - format: 'csv' or 'xlsx'
    - campaign_id: Optional campaign filter
    - start_date: Optional start date
    - end_date: Optional end date
    
    Returns:
    - File download with unsubscribed emails
    
    Columns include:
    - Email, First Name, Last Name
    - Campaign ID, Subject
    - Sent At, Unsubscribed (Yes/No)
    - Unsubscribed At
    """
    service = ExportService(db)
    
    try:
        return await service.export_unsubscribed(
            format=format,
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        logger.error(f"Error exporting unsubscribed emails: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export: {str(e)}"
        )


# ==============================================================================
# ALL EMAILS EXPORT
# ==============================================================================

@router.get(
    "/email-logs",
    summary="Export Email Logs",
    description="Export email logs based on status filter",
    response_class=StreamingResponse
)
async def export_email_logs(
    format: str = Query("csv", regex="^(csv|xlsx)$", description="Export format: csv or xlsx"),
    status: Optional[str] = Query(None, description="Filter by status: all, delivered, opened, failed, bounced"),
    search: Optional[str] = Query(None, description="Search query"),
    campaign_id: Optional[int] = Query(None, description="Filter by campaign ID"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db)
):
    """
    Export email logs with filters
    
    Query Parameters:
    - format: 'csv' or 'xlsx'
    - status: 'all', 'delivered', 'opened', 'failed', 'bounced' (default: all)
    - search: Search in email/subject/campaign
    - campaign_id: Optional campaign filter
    - start_date: Optional start date
    - end_date: Optional end date
    """
    service = ExportService(db)
    
    try:
        # Default to 'all' if no status specified
        export_status = status if status and status != 'all' else 'all'
        
        return await service.export_emails(
            status=export_status,
            format=format,
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        logger.error(f"Error exporting email logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export: {str(e)}"
        )


@router.get(
    "/all",
    summary="Export All Emails",
    description="Export complete email data with all metrics",
    response_class=StreamingResponse
)
async def export_all(
    format: str = Query("xlsx", regex="^(csv|xlsx)$", description="Export format (xlsx recommended)"),
    campaign_id: Optional[int] = Query(None, description="Filter by campaign ID"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db)
):
    """
    Export all emails with complete data
    
    Query Parameters:
    - format: 'csv' or 'xlsx' (xlsx recommended for full data)
    - campaign_id: Optional campaign filter
    - start_date: Optional start date
    - end_date: Optional end date
    
    Returns:
    - File download with all email data
    
    Columns include:
    - Email, First Name, Last Name
    - Campaign ID, Subject
    - Sent At, Delivery Status
    - Delivered At, Opened, Opened At, Open Count
    - Bounced, Bounce Type, Bounce Reason, Bounced At
    - Unsubscribed, Unsubscribed At
    - Tracking ID, IP Address
    """
    service = ExportService(db)
    
    try:
        return await service.export_all(
            format=format,
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        logger.error(f"Error exporting all emails: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export: {str(e)}"
        )


# ==============================================================================
# CAMPAIGN SUMMARY REPORT
# ==============================================================================

@router.get(
    "/campaign-report/{campaign_id}",
    summary="Export Campaign Summary Report",
    description="Export comprehensive campaign report with summary and details",
    response_class=StreamingResponse
)
async def export_campaign_report(
    campaign_id: int,
    format: str = Query("xlsx", regex="^(csv|xlsx)$", description="Export format"),
    db: Session = Depends(get_db)
):
    """
    Export comprehensive campaign report
    
    Path Parameters:
    - campaign_id: Campaign ID
    
    Query Parameters:
    - format: 'csv' or 'xlsx' (xlsx includes summary sheet)
    
    Returns:
    - Excel file with two sheets:
      1. Summary: Campaign statistics
      2. Email Details: Complete email data
    - CSV file with detailed data only
    
    Summary includes:
    - Campaign name, total emails, sent/delivered/opened/bounced/unsubscribed counts
    - Delivery rate, open rate, bounce rate
    - Campaign status and timestamps
    """
    service = ExportService(db)
    
    try:
        return await service.export_campaign_summary(
            campaign_id=campaign_id,
            format=format
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error exporting campaign report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export: {str(e)}"
        )


# ==============================================================================
# EXPORT PREVIEW
# ==============================================================================

@router.get(
    "/preview/{status}",
    summary="Preview Export Data",
    description="Get preview of export data before downloading"
)
async def get_export_preview(
    status: str,
    campaign_id: Optional[int] = Query(None, description="Filter by campaign ID"),
    limit: int = Query(10, ge=1, le=50, description="Number of preview rows"),
    db: Session = Depends(get_db)
):
    """
    Get preview of export data
    
    Path Parameters:
    - status: Email status ('delivered', 'opened', 'bounced', 'unsubscribed', 'all')
    
    Query Parameters:
    - campaign_id: Optional campaign filter
    - limit: Number of preview rows (1-50)
    
    Returns:
    - Preview data with total count
    
    Use this before exporting to:
    - Verify filters are correct
    - Check data availability
    - Estimate export size
    """
    service = ExportService(db)
    
    try:
        preview = service.get_export_preview(
            status=status,
            campaign_id=campaign_id,
            limit=limit
        )
        return preview
    except Exception as e:
        logger.error(f"Error getting export preview: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get preview: {str(e)}"
        )


# ==============================================================================
# HEALTH CHECK
# ==============================================================================

@router.get(
    "/health",
    summary="Export API Health Check",
    description="Check if export API is operational"
)
async def export_health_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Health check for export API
    
    Returns:
    - Status of export system
    - Available export formats
    - Database connectivity
    """
    try:
        from app.models.email_log import EmailLog
        
        # Quick database check
        total_emails = db.query(EmailLog).count()
        
        return {
            "status": "healthy",
            "service": "Export API",
            "database": "connected",
            "total_emails": total_emails,
            "supported_formats": ["csv", "xlsx"],
            "export_types": [
                "delivered",
                "opened",
                "bounced",
                "unsubscribed",
                "all"
            ]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Export API",
            "error": str(e)
        }
