"""
Fix campaign statistics by counting from email_logs
"""
import sys
sys.path.append('.')

from app.db.database import SessionLocal
from app.models.campaign import Campaign
from app.models.email_log import EmailLog
from sqlalchemy import func

def fix_campaign_stats():
    db = SessionLocal()
    
    try:
        campaigns = db.query(Campaign).all()
        
        for campaign in campaigns:
            # Count from email_logs
            logs_query = db.query(EmailLog).filter(EmailLog.campaign_id == campaign.id)
            
            sent_count = logs_query.count()
            delivered_count = logs_query.filter(EmailLog.delivery_status == "delivered").count()
            failed_count = logs_query.filter(EmailLog.delivery_status == "failed").count()
            opened_count = logs_query.filter(EmailLog.opened == True).count()
            bounced_count = logs_query.filter(EmailLog.bounced == True).count()
            unsubscribed_count = logs_query.filter(EmailLog.unsubscribed == True).count()
            
            # Update campaign
            campaign.sent_count = sent_count
            campaign.delivered_count = delivered_count
            campaign.failed_count = failed_count
            campaign.opened_count = opened_count
            campaign.bounced_count = bounced_count
            campaign.unsubscribed_count = unsubscribed_count
            
            print(f"Campaign: {campaign.campaign_name}")
            print(f"  Sent: {sent_count}, Delivered: {delivered_count}, Opened: {opened_count}")
            print(f"  Failed: {failed_count}, Bounced: {bounced_count}, Unsubscribed: {unsubscribed_count}")
        
        db.commit()
        print("\n✓ Campaign statistics fixed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_campaign_stats()
