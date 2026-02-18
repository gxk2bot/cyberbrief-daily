#!/usr/bin/env python3
"""
Send CyberBrief newsletter via message tool
"""

import sys
from cyberbrief_live import CyberBriefLive

def send_newsletter_email(to_email: str):
    """Generate and send newsletter via message tool"""
    
    # Generate live newsletter
    brief = CyberBriefLive()
    newsletter_content = brief.generate_newsletter()
    
    # Format for email
    subject = f"CyberBrief Daily - Executive Threat Intelligence - February 18, 2026"
    
    return newsletter_content, subject

if __name__ == "__main__":
    content, subject = send_newsletter_email("casey.l.beaumont@gmail.com")
    print("Subject:", subject)
    print("\nContent:")
    print(content)