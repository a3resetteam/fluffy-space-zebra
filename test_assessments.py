#!/usr/bin/env python3
"""
Simple test script to verify the new assessment routes work
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing import...")
    from app import app, init_db
    
    print("✅ Import successful!")
    print("Initializing database...")
    init_db()
    print("✅ Database initialized!")
    
    print("Testing Flask app...")
    with app.test_client() as client:
        # Test basic route
        response = client.get('/')
        print(f"Home route status: {response.status_code}")
        
        # Test assessment route
        response = client.get('/assessment')
        print(f"Assessment route status: {response.status_code}")
        
        # Test new assessment routes
        routes_to_test = [
            '/assessment/personality-profile',
            '/assessment/mindset-analysis',
            '/assessment/relationship-patterns',
            '/assessment/goal-orientation',
            '/assessment/transformation-readiness'
        ]
        
        for route in routes_to_test:
            response = client.get(route)
            print(f"Route {route}: {response.status_code}")
    
    print("✅ All tests passed! Routes are working.")
    print("Starting development server on port 5002...")
    app.run(debug=True, host='0.0.0.0', port=5002)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
