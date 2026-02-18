#!/usr/bin/env python3
"""
Test script for CyberBrief Daily
Runs a dry-run without sending emails
"""

import json
import sys
from pathlib import Path
from cyberbrief import CyberBrief

def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    
    config_path = Path("config.json")
    if not config_path.exists():
        print("❌ config.json not found. Copy from config.example.json and edit.")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print("✅ Configuration loaded successfully")
        
        # Check required fields
        required_fields = [
            "email.smtp_server",
            "email.username", 
            "email.to_addrs",
            "openai.api_key"
        ]
        
        for field in required_fields:
            keys = field.split('.')
            value = config
            for key in keys:
                value = value.get(key)
            if not value:
                print(f"❌ Missing required field: {field}")
                return False
        
        print("✅ All required configuration fields present")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_sources():
    """Test source connectivity"""
    print("\nTesting source connectivity...")
    
    try:
        brief = CyberBrief()
        
        # Test BleepingComputer RSS
        print("Testing BleepingComputer RSS...")
        articles = brief.fetch_bleepingcomputer_articles()
        print(f"✅ Found {len(articles)} recent articles from BleepingComputer")
        
        # Test CISA KEV
        print("Testing CISA KEV feed...")
        vulns = brief.fetch_cisa_kev()
        print(f"✅ Found {len(vulns)} recent vulnerabilities from CISA")
        
        # Test security blogs
        print("Testing security blog discovery...")
        blogs = brief.discover_active_security_blogs()
        print(f"✅ Found {len(blogs)} active security blogs")
        
        return True
        
    except Exception as e:
        print(f"❌ Source connectivity error: {e}")
        return False

def test_newsletter_generation():
    """Test newsletter generation without sending"""
    print("\nTesting newsletter generation...")
    
    try:
        brief = CyberBrief()
        newsletter = brief.generate_newsletter()
        
        # Save test newsletter
        test_file = "test_newsletter.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(newsletter)
        
        print(f"✅ Newsletter generated successfully")
        print(f"✅ Test newsletter saved to {test_file}")
        print(f"Newsletter length: {len(newsletter)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Newsletter generation error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 CyberBrief Daily Test Suite")
    print("=" * 40)
    
    tests = [
        ("Configuration", test_config),
        ("Source Connectivity", test_sources), 
        ("Newsletter Generation", test_newsletter_generation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("🎯 Test Results Summary")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! CyberBrief Daily is ready.")
        print("Run 'python cyberbrief.py' to generate and send your first newsletter.")
    else:
        print("\n⚠️  Some tests failed. Check configuration and network connectivity.")
        sys.exit(1)

if __name__ == "__main__":
    main()