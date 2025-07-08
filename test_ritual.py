#!/usr/bin/env python3
"""
Test ritual creation functionality
"""

import requests
import sqlite3

def test_ritual_creation():
    """Test the ritual creation flow"""
    
    # Get test user credentials
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
    print("🔐 Logging in...")
    login_response = session.post('http://localhost:5000/login', data={
        'email': email,
        'password': password
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Test ritual creation
    print("🎭 Creating ritual...")
    ritual_data = {
        'birthday': '1990-01-01',
        'mood': 'calm',
        'environment': 'indoor',
        'duration': '15',
        'time_of_day': 'morning',
        'ritual_need': 'peace',
        'movement_type': 'restorative_yoga',
        'body_areas': ['neck_shoulders', 'spine_back'],
        'breathing_style': 'calming_breath',
        'intensity_level': 'gentle_restoration',
        'ritual_items': ['candles'],
        'elemental_focus': 'water',
        'focus_area': 'mindfulness'
    }
    
    ritual_response = session.post('http://localhost:5000/ritual-session', data=ritual_data)
    
    if ritual_response.status_code == 200:
        print("✅ Ritual creation successful")
        
        # Check if it contains HTML or raw code
        if '<html' in ritual_response.text and 'ritual-step' in ritual_response.text:
            print("✅ Ritual session page rendered properly")
        elif '{{' in ritual_response.text or 'ritual_data' in ritual_response.text:
            print("❌ Page shows raw template code - template rendering issue")
        else:
            print("⚠️  Unexpected response format")
            
        # Save response for inspection
        with open('ritual_test_response.html', 'w') as f:
            f.write(ritual_response.text)
        print("📄 Response saved to ritual_test_response.html")
        
    else:
        print(f"❌ Ritual creation failed: {ritual_response.status_code}")
        print(f"Response: {ritual_response.text[:200]}...")

if __name__ == '__main__':
    test_ritual_creation()
