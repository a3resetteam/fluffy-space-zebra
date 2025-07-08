#!/usr/bin/env python3
"""
Test admin panel functionality
"""
import requests
import json

def test_admin_endpoints():
    base_url = "http://localhost:5000"
    
    print("🔍 Testing Admin Panel Endpoints...")
    
    # Test 1: Try accessing admin panel without login
    print("\n1. Testing admin panel access without login...")
    response = requests.get(f"{base_url}/admin")
    print(f"Status: {response.status_code}")
    if response.status_code == 302:
        print("✅ Redirects to login (expected)")
    
    # Test 2: Try admin login
    print("\n2. Testing admin login...")
    login_data = {
        'email': 'marlexus@a3reset.com',
        'password': 'A3password123'
    }
    
    session = requests.Session()
    response = session.post(f"{base_url}/admin/login", data=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 302:
        print("✅ Login successful (redirected)")
        
        # Test 3: Try accessing admin panel after login
        print("\n3. Testing admin panel access after login...")
        response = session.get(f"{base_url}/admin")
        print(f"Admin Panel Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Admin panel accessible")
            
            # Test 4: Test an admin action endpoint
            print("\n4. Testing admin action endpoint...")
            response = session.post(f"{base_url}/admin/process-failed-payments")
            print(f"Action Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Action response: {data}")
                except:
                    print("❌ Response is not JSON")
            else:
                print(f"❌ Action failed with status {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print("❌ Cannot access admin panel")
    else:
        print("❌ Login failed")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_admin_endpoints()
