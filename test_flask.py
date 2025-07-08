#!/usr/bin/env python3
"""
Test basic Flask app functionality
"""

try:
    from app import app, init_db
    print("✅ App imported successfully")
    
    init_db()
    print("✅ Database initialized")
    
    with app.test_client() as client:
        response = client.get('/login')
        print(f"✅ Login route test: {response.status_code}")
        
    print("✅ Basic Flask test passed")
    
    # Try to run the app
    print("🚀 Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5000)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
