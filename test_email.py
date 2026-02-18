#!/usr/bin/env python3
"""
Test email functionality for CyberBrief Daily
"""

import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

def test_email():
    """Test Gmail SMTP connection"""
    
    # Load environment
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    gmail_user = os.getenv('GMAIL_USER', '')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD', '')
    
    if not gmail_user or not gmail_password:
        print("❌ Email credentials not found in environment variables")
        return False
    
    print(f"📧 Testing email connection...")
    print(f"From: {gmail_user}")
    print(f"Password: {'*' * len(gmail_password)}")
    
    try:
        # Create test message
        test_content = f"""
🧪 CyberBrief Daily Email Test

This is a test message from your CyberBrief Daily system.

✅ Gmail SMTP connection: Working
✅ Authentication: Successful
✅ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Your daily cybersecurity newsletter is ready to deliver!

--
CyberBrief Daily Test System
        """
        
        msg = MIMEText(test_content)
        msg['Subject'] = f"🧪 CyberBrief Daily Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        msg['From'] = gmail_user
        msg['To'] = "casey.l.beaumont@gmail.com"
        
        # Connect to Gmail SMTP
        print("🔌 Connecting to Gmail SMTP...")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            print("🔐 Starting TLS...")
            server.starttls()
            
            print("🔑 Authenticating...")
            server.login(gmail_user, gmail_password)
            
            print("📤 Sending test email...")
            server.send_message(msg, to_addrs=["casey.l.beaumont@gmail.com"])
        
        print("✅ Test email sent successfully!")
        print(f"📬 Check casey.l.beaumont@gmail.com for the test message")
        return True
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        
        if "Username and Password not accepted" in str(e):
            print("\n🔧 Possible solutions:")
            print("1. Enable 2-Factor Authentication on gxk2bot@gmail.com")  
            print("2. Generate an App Password instead of using the regular password")
            print("3. Go to: https://myaccount.google.com/apppasswords")
            print("4. Create app password for 'Mail' and use that instead")
        elif "Less secure app access" in str(e):
            print("\n🔧 Gmail security settings:")
            print("1. Go to https://myaccount.google.com/security")
            print("2. Enable 2-Step Verification") 
            print("3. Generate an App Password for email")
            
        return False

if __name__ == "__main__":
    print("🧪 CyberBrief Daily Email Test")
    print("=" * 40)
    success = test_email()
    exit(0 if success else 1)