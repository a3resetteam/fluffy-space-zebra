#!/usr/bin/env python3
"""
Test script to verify the improved ritual session UI and timer functionality.
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_ritual_creation_and_ui():
    """Test creating a ritual and accessing the session page."""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("🔮 Testing Ritual UI and Timer Functionality")
    print("=" * 50)
    
    # Test 1: Login with test user
    print("1. Logging in with test user...")
    login_data = {
        'email': 'test@oracle.com',
        'password': 'password123'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"   Login status: {response.status_code}")
    
    if response.status_code == 302:
        print("   ✅ Login successful - redirected to dashboard")
    else:
        print("   ❌ Login failed")
        return False
    
    # Test 2: Create a new ritual with advanced options
    print("\n2. Creating a new ritual with advanced options...")
    ritual_data = {
        'intention': 'Transform my confidence and release limiting beliefs',
        'duration': '15',
        'movement_type': 'full_body_flow',
        'breathing_style': 'box_breathing',
        'body_areas': ['core', 'heart_chest'],
        'intensity': 'moderate'
    }
    
    response = session.post(f"{BASE_URL}/ritual-session", data=ritual_data)
    print(f"   Ritual creation status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Ritual created successfully")
        
        # Check if the response contains the expected elements
        content = response.text
        
        # Check for timer elements
        if 'countdownTimer' in content:
            print("   ✅ Timer element found in HTML")
        else:
            print("   ❌ Timer element missing")
        
        # Check for ritual steps
        if 'ritual-step' in content:
            print("   ✅ Ritual steps found in HTML")
        else:
            print("   ❌ Ritual steps missing")
        
        # Check for improved styling
        if 'step-emoji' in content and 'step-benefits' in content:
            print("   ✅ Enhanced styling elements found")
        else:
            print("   ❌ Enhanced styling elements missing")
        
        # Check for JavaScript functionality
        if 'startRitual()' in content:
            print("   ✅ Updated JavaScript functions found")
        else:
            print("   ❌ Updated JavaScript functions missing")
        
        # Save a sample of the rendered HTML for inspection
        with open('/workspaces/codespaces-blank/ritual_session_sample.html', 'w') as f:
            f.write(content)
        print("   📄 Full HTML saved to ritual_session_sample.html for inspection")
        
    else:
        print(f"   ❌ Ritual creation failed with status {response.status_code}")
        return False
    
    print("\n🎉 UI Test Complete!")
    print("\nTo manually test the timer and UI:")
    print("1. Open http://localhost:5000 in your browser")
    print("2. Login with test@oracle.com/password123") 
    print("3. Go to Ritual Creator")
    print("4. Fill out the form and click 'Create My Ritual'")
    print("5. Click 'Start Ritual' to test the timer")
    print("6. Verify that:")
    print("   - Timer counts down properly")
    print("   - Steps are visually boxed and clean")
    print("   - Active step is highlighted")
    print("   - Progress ring updates")
    print("   - Step transitions work smoothly")
    
    return True

if __name__ == "__main__":
    test_ritual_creation_and_ui()
