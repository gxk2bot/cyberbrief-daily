#!/usr/bin/env python3
"""
Test the enhanced CyberBrief Daily format
Shows preview without sending email
"""

from cyberbrief_enhanced import CyberBriefEnhanced
import sys

def test_enhanced():
    """Test the enhanced format"""
    print("🧪 Testing CyberBrief Daily Enhanced Format")
    print("=" * 50)
    
    try:
        # Initialize system
        brief = CyberBriefEnhanced()
        
        # Generate newsletter
        print("🚀 Generating enhanced newsletter...")
        newsletter = brief.generate_newsletter()
        
        # Save test version
        with open('test_enhanced_preview.txt', 'w', encoding='utf-8') as f:
            f.write(newsletter)
        
        print("✅ Enhanced newsletter generated successfully!")
        print(f"📄 Preview saved to: test_enhanced_preview.txt")
        
        # Show preview
        print("\n" + "="*60)
        print("ENHANCED CYBERBRIEF DAILY - PREVIEW")
        print("="*60)
        print(newsletter)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced()
    sys.exit(0 if success else 1)