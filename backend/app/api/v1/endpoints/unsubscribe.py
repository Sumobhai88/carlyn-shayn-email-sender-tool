"""
Unsubscribe endpoints
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.database import get_db
from app.models.email_log import EmailLog
from app.models.campaign import Campaign

router = APIRouter()


@router.get("/unsubscribe/{tracking_id}", response_class=HTMLResponse)
async def unsubscribe_page(
    tracking_id: str,
    db: Session = Depends(get_db)
):
    """
    Show unsubscribe confirmation page
    """
    # Find email log
    email_log = db.query(EmailLog).filter(
        EmailLog.tracking_id == tracking_id
    ).first()
    
    if not email_log:
        return HTMLResponse(content="""
            <html>
            <head><title>Invalid Link</title></head>
            <body style='font-family: Arial; text-align: center; padding: 50px;'>
                <h1>Invalid Unsubscribe Link</h1>
                <p>This unsubscribe link is not valid.</p>
            </body>
            </html>
        """, status_code=404)
    
    # Check if already unsubscribed
    already_unsubscribed = email_log.unsubscribed
    
    html_content = f"""
    <html>
    <head>
        <title>Unsubscribe</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 10px;
                padding: 40px;
                max-width: 500px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
            }}
            h1 {{
                color: #333;
                margin-bottom: 20px;
            }}
            p {{
                color: #666;
                line-height: 1.6;
                margin-bottom: 30px;
            }}
            .email {{
                background: #f5f5f5;
                padding: 10px;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
                color: #333;
            }}
            button {{
                background: #dc3545;
                color: white;
                border: none;
                padding: 15px 40px;
                font-size: 16px;
                border-radius: 5px;
                cursor: pointer;
                transition: background 0.3s;
            }}
            button:hover {{
                background: #c82333;
            }}
            .success {{
                color: #28a745;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {"<h1 class='success'>✓ Already Unsubscribed</h1>" if already_unsubscribed else "<h1>Unsubscribe from Emails</h1>"}
            <p>Email address:</p>
            <div class="email">{email_log.recipient_email}</div>
            
            {f"<p>You have already unsubscribed from our mailing list on {email_log.unsubscribed_at.strftime('%B %d, %Y') if email_log.unsubscribed_at else 'an earlier date'}.</p>" if already_unsubscribed else 
            f'''<p>Are you sure you want to unsubscribe from our mailing list?</p>
            <form method="POST" action="/api/v1/unsubscribe/{tracking_id}/confirm">
                <button type="submit">Confirm Unsubscribe</button>
            </form>
            <p style="font-size: 12px; color: #999; margin-top: 20px;">You will no longer receive emails from this campaign.</p>'''}
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.post("/unsubscribe/{tracking_id}/confirm", response_class=HTMLResponse)
async def confirm_unsubscribe(
    tracking_id: str,
    db: Session = Depends(get_db)
):
    """
    Process unsubscribe request
    """
    # Find email log
    email_log = db.query(EmailLog).filter(
        EmailLog.tracking_id == tracking_id
    ).first()
    
    if not email_log:
        return HTMLResponse(content="""
            <html>
            <head><title>Invalid Link</title></head>
            <body style='font-family: Arial; text-align: center; padding: 50px;'>
                <h1>Invalid Unsubscribe Link</h1>
            </body>
            </html>
        """, status_code=404)
    
    # Mark as unsubscribed
    if not email_log.unsubscribed:
        email_log.unsubscribed = True
        email_log.unsubscribed_at = datetime.now(timezone.utc)
        
        # Update campaign count
        campaign = db.query(Campaign).filter(
            Campaign.id == email_log.campaign_id
        ).first()
        
        if campaign:
            campaign.unsubscribed_count = (campaign.unsubscribed_count or 0) + 1
        
        db.commit()
    
    # Show success page
    html_content = f"""
    <html>
    <head>
        <title>Unsubscribed Successfully</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 10px;
                padding: 40px;
                max-width: 500px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
            }}
            h1 {{
                color: #28a745;
                margin-bottom: 20px;
            }}
            p {{
                color: #666;
                line-height: 1.6;
            }}
            .email {{
                background: #f5f5f5;
                padding: 10px;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✓ Unsubscribed Successfully</h1>
            <p>You have been removed from our mailing list.</p>
            <div class="email">{email_log.recipient_email}</div>
            <p>You will no longer receive emails from this campaign.</p>
            <p style="font-size: 12px; color: #999; margin-top: 30px;">
                If you believe this was a mistake, please contact us.
            </p>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
