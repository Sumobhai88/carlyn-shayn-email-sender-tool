"""
Manual tracking test script
Use this to test tracking without ngrok
"""
import requests
import json

print("=" * 60)
print("MANUAL TRACKING TEST")
print("=" * 60)

# Get latest email log
print("\n1. Fetching latest email logs...")
try:
    response = requests.get('http://const API_URL = import.meta.env.VITE_API_URL/api/v1/analytics/email-logs?limit=5')
    data = response.json()
    
    if data.get('email_logs') and len(data['email_logs']) > 0:
        print(f"   Found {len(data['email_logs'])} email logs")
        
        # Show first email
        log = data['email_logs'][0]
        print(f"\n   Latest Email:")
        print(f"   - Recipient: {log['recipient_email']}")
        print(f"   - Subject: {log['subject']}")
        print(f"   - Tracking ID: {log.get('tracking_id', 'N/A')}")
        print(f"   - Opened: {log.get('opened', False)}")
        print(f"   - Sent At: {log.get('sent_at', 'N/A')}")
        
        # Ask user if they want to mark as opened
        tracking_id = log.get('tracking_id')
        if tracking_id and not log.get('opened'):
            print(f"\n2. Testing tracking pixel...")
            print(f"   Calling: /api/v1/tracking/open/{tracking_id}")
            
            # Simulate tracking pixel request
            tracking_response = requests.get(
                f'http://const API_URL = import.meta.env.VITE_API_URL/api/v1/tracking/open/{tracking_id}',
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'
                }
            )
            
            if tracking_response.status_code == 200:
                print(f"   ✅ Tracking pixel loaded successfully!")
                
                # Check stats
                print(f"\n3. Checking tracking stats...")
                stats_response = requests.get(
                    f'http://const API_URL = import.meta.env.VITE_API_URL/api/v1/tracking/stats/{tracking_id}'
                )
                stats = stats_response.json()
                
                print(f"\n   Tracking Stats:")
                print(f"   - Opened: {stats.get('opened', False)}")
                print(f"   - Opened At: {stats.get('opened_at', 'N/A')}")
                print(f"   - Open Count: {stats.get('open_count', 0)}")
                
                print(f"\n4. Checking analytics...")
                analytics_response = requests.get('http://const API_URL = import.meta.env.VITE_API_URL/api/v1/analytics/email-logs?limit=1')
                analytics = analytics_response.json()
                if analytics.get('email_logs'):
                    log_updated = analytics['email_logs'][0]
                    print(f"   - Email Opened: {log_updated.get('opened', False)}")
                    print(f"   - Opened At: {log_updated.get('opened_at', 'N/A')}")
                
                print(f"\n✅ SUCCESS! Tracking is working!")
                print(f"\nNow check:")
                print(f"  1. Dashboard - Open rate should be updated")
                print(f"  2. Email Analytics - Eye icon should appear")
                
            else:
                print(f"   ❌ Error: {tracking_response.status_code}")
        elif log.get('opened'):
            print(f"\n   ℹ️  This email is already marked as opened")
            print(f"   Opened at: {log.get('opened_at')}")
        else:
            print(f"\n   ❌ No tracking ID found")
    else:
        print("   ❌ No email logs found. Send a campaign first!")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
