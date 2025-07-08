#!/usr/bin/env python3
"""
Test script to verify the AI coach API functionality
"""

import requests
import json
import sys
import os
import time

def test_ai_coach_api():
    """Test if the AI coach API endpoint works"""
    print("🔍 Testing AI Coach API...")
    print("-" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # Check if the AI coach page loads
        response = requests.get(f"{base_url}/ai-coach")
        if response.status_code == 200:
            print("✅ AI Coach page loads successfully")
            if "AI Situationship Coach" not in response.text:
                print("⚠️ Page loaded but 'AI Situationship Coach' text not found - might be redirected to login")
        else:
            print(f"❌ AI Coach page failed to load: Status {response.status_code}")
            return False
        
        # Test API endpoint without authentication (should fail)
        chat_data = {
            "message": "Test message",
            "coach_type": "supportive",
            "conversation_history": []
        }
        
        response = requests.post(
            f"{base_url}/ai-coach/chat", 
            json=chat_data
        )
        
        if response.status_code == 401:
            print("✅ Authentication check working - unauthorized access rejected")
        else:
            print(f"❌ Authentication check failed: Status {response.status_code}")
            return False
            
        print("\n✅ Basic API tests completed")
        print("-" * 50)
        print("To fully test the AI coach with authentication:")
        print("1. Log in to the platform")
        print("2. Navigate to the AI Coach page")
        print("3. Select a coach type and send a message")
        print("4. Check browser console for any API errors")
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI Coach API: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_coach_api()
    sys.exit(0 if success else 1)
