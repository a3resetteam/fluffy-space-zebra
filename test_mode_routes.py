#!/usr/bin/env python3
"""
Test mode routes with authentication
"""

import requests
import sqlite3

def test_mode_routes():
    """Test all mode routes work with authentication"""
    
    # Get test user
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM users WHERE email LIKE "test_%@oracle.test" ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        print("❌ No test user found")
        return
    
    email = result[0]
    password = "testpassword123"
    
    # Create session
    session = requests.Session()
    
    # Login
    login_response = session.post('http://localhost:5000/login', data={
        'email': email,
        'password': password
    })
    
    if login_response.status_code == 200 and 'MYA3Reset' in login_response.text:
        print("✅ Login successful")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    # Test mode routes
    routes_to_test = [
        '/mode/alpha-elite',
        '/situationship', 
        '/assessment',
        '/ritual-creator'
    ]
    
    print("\n🧪 Testing mode routes:")
    for route in routes_to_test:
        try:
            response = session.get(f'http://localhost:5000{route}')
            if response.status_code == 200:
                print(f"✅ {route}: Status {response.status_code} - Working")
            else:
                print(f"❌ {route}: Status {response.status_code} - Failed")
        except Exception as e:
            print(f"❌ {route}: Error - {e}")
    
    print(f"\n📝 Test completed. You can manually test by logging in with:")
    print(f"   Email: {email}")
    print(f"   Password: {password}")

if __name__ == '__main__':
    test_mode_routes()
