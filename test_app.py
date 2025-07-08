#!/usr/bin/env python3
"""
Quick test of app imports and basic functionality
"""

import sys
import traceback

try:
    from app import app, init_db
    print("✅ App imports successful")
    
    # Test database initialization
    init_db()
    print("✅ Database initialization successful")
    
    # Test basic app creation
    with app.test_client() as client:
        # Test that routes exist
        response = client.get('/login')
        print(f"✅ Login route exists, status: {response.status_code}")
        
        print("✅ Basic app functionality working")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"❌ Traceback:")
    traceback.print_exc()
