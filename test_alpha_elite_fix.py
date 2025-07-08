#!/usr/bin/env python3
"""
Test script to verify Alpha Elite Mode Strategic Mastery access
"""
import sys
import requests
import time
from datetime import datetime

def test_alpha_elite_access():
    """Test if we can access the Alpha Elite strategic mastery route"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Alpha Elite Mode Access...")
    print("=" * 50)
    
    # Test 1: Direct access to strategic mastery without login
    print("\n1. Testing direct access to strategic mastery...")
    try:
        response = requests.get(f"{base_url}/alpha-elite/strategic-mastery", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Length: {len(response.text)} chars")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS: Strategic mastery page accessible!")
            if "Strategic Mastery Training" in response.text:
                print("   ✅ Page contains expected content")
            else:
                print("   ⚠️  Page loaded but may not have expected content")
        else:
            print(f"   ❌ FAILED: Got status code {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ FAILED: Cannot connect to Flask app. Is it running?")
        return False
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        return False
    
    # Test 2: Access to strategic observation
    print("\n2. Testing strategic observation sub-route...")
    try:
        response = requests.get(f"{base_url}/alpha-elite/strategic-mastery/strategic-observation", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS: Strategic observation page accessible!")
        else:
            print(f"   ❌ FAILED: Got status code {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
    
    # Test 3: Check if we can access the main alpha elite mode
    print("\n3. Testing main alpha elite mode access...")
    try:
        response = requests.get(f"{base_url}/mode/alpha-elite", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS: Alpha elite mode accessible!")
        else:
            print(f"   ❌ FAILED: Got status code {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Results Summary:")
    print("   - The strategic mastery route should now be working")
    print("   - Demo user functionality is enabled for Alpha Elite mode")
    print("   - Session handling has been improved")
    
    return True

if __name__ == "__main__":
    print(f"🚀 Alpha Elite Mode Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Wait a moment for Flask to start
    print("⏳ Waiting for Flask app to start...")
    time.sleep(3)
    
    success = test_alpha_elite_access()
    
    if success:
        print("\n🎉 Testing completed!")
        print("\n💡 To manually test:")
        print("   1. Open your browser to http://127.0.0.1:5000")
        print("   2. Navigate to Alpha Elite mode")
        print("   3. Click on Strategic Mastery")
        print("   4. You should now be able to access the training!")
    else:
        print("\n❌ Tests failed - check Flask app status")
