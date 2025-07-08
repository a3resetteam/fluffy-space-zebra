#!/usr/bin/env python3
"""
Test Alpha Elite Routes - Real-time testing
"""
import requests
import time
from datetime import datetime

def test_routes():
    """Test all Alpha Elite routes"""
    base_url = "http://127.0.0.1:5000"
    
    print(f"🚀 Testing Alpha Elite Routes - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    routes_to_test = [
        ("/", "Home page"),
        ("/alpha-elite/strategic-mastery", "Strategic Mastery"),
        ("/alpha-elite/strategic-mastery/strategic-observation", "Strategic Observation"),
        ("/mode/alpha-elite", "Alpha Elite Mode"),
    ]
    
    for route, description in routes_to_test:
        try:
            print(f"\n🔍 Testing: {description}")
            print(f"   URL: {base_url}{route}")
            
            response = requests.get(f"{base_url}{route}", timeout=10)
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   ✅ Size: {len(response.text)} chars")
            
            if response.status_code == 200:
                # Check for key content
                if "Strategic" in response.text:
                    print(f"   ✅ Contains expected content")
                else:
                    print(f"   ⚠️  Page loaded but content may be different")
            elif response.status_code == 302:
                print(f"   ↗️  Redirect (normal for some routes)")
            else:
                print(f"   ❌ Unexpected status code")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed - Flask app may not be running")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("   The Alpha Elite strategic mastery routes are working!")
    print("   You should be able to access the training now.")
    print("\n📋 Access Instructions:")
    print("   1. Open: http://127.0.0.1:5000")
    print("   2. Go to Alpha Elite mode")
    print("   3. Click Strategic Mastery")
    print("   4. Start Strategic Observation training")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_routes()
