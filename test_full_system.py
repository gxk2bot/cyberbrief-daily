#!/usr/bin/env python3
"""
Test the full CyberBrief Daily system including email
"""

from cyberbrief_production import CyberBriefProduction
import sys

def test_system():
    """Test the complete system"""
    print("🧪 Testing Complete CyberBrief Daily System")
    print("=" * 50)
    
    try:
        # Initialize the system
        print("🔧 Initializing CyberBrief Daily...")
        brief = CyberBriefProduction()
        
        # Test configuration
        config = brief.config
        if config.get('email', {}).get('username'):
            print(f"✅ Email configured: {config['email']['username']}")
        else:
            print("⚠️  Email not configured - will save to file only")
        
        print(f"✅ Recipient: {config.get('email', {}).get('to_addrs', ['Not set'])}")
        
        # Run the system
        print("\n🚀 Generating newsletter with live data...")
        success = brief.run()
        
        if success:
            print("\n✅ CyberBrief Daily test completed successfully!")
            print("\n📋 What happened:")
            print("• Fetched real threat data from BleepingComputer")
            print("• Retrieved CISA Known Exploitable Vulnerabilities")
            print("• Collected security blog posts")
            print("• Generated executive-focused newsletter")
            print("• Attempted email delivery (if configured)")
            print("• Saved backup to newsletters/ directory")
            
            return True
        else:
            print("\n❌ System test failed - check logs")
            return False
            
    except Exception as e:
        print(f"\n❌ System test error: {e}")
        return False

if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)