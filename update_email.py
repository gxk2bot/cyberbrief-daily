#!/usr/bin/env python3
"""
Update email configuration with app password
"""

import os

def update_email_config(app_password):
    """Update .env file with the Gmail app password"""
    
    env_content = f"""GMAIL_USER=gxk2bot@gmail.com
GMAIL_APP_PASSWORD={app_password}
OPENAI_API_KEY=
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Updated .env file with new app password")
    print("🔒 Credentials stored securely in .env")

if __name__ == "__main__":
    print("📧 Gmail App Password Setup")
    print("=" * 30)
    
    app_password = input("Enter the 16-character Gmail app password: ").strip()
    
    if len(app_password) == 16 and app_password.replace(' ', '').isalnum():
        # Remove spaces if user included them
        clean_password = app_password.replace(' ', '')
        update_email_config(clean_password)
        
        print("\n🧪 Testing email with new password...")
        os.system("python3 test_email.py")
        
    else:
        print("❌ Invalid app password format")
        print("Expected: 16 characters like 'abcdefghijklmnop'")