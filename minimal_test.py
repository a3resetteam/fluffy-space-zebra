#!/usr/bin/env python3
"""
Minimal test of strategic_mastery function
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, '/workspaces/codespaces-blank')

def test_strategic_mastery_function():
    """Test the strategic mastery function in isolation"""
    try:
        print("🧪 Testing strategic_mastery function...")
        
        # Import the Flask app
        from app import app, init_db, strategic_mastery
        
        print("✅ Successfully imported app and functions")
        
        # Initialize database
        init_db()
        print("✅ Database initialized")
        
        # Test the function with Flask context
        with app.test_client() as client:
            with client.session_transaction() as sess:
                # Simulate a session with demo user
                sess['customer_id'] = 'DEMO-USER'
                sess['username'] = 'Demo User'
            
            print("🔄 Testing strategic mastery route...")
            response = client.get('/alpha-elite/strategic-mastery')
            
            print(f"✅ Response status: {response.status_code}")
            print(f"✅ Response length: {len(response.data)} bytes")
            
            if response.status_code == 200:
                print("🎉 SUCCESS! Strategic mastery route is working!")
                return True
            else:
                print(f"❌ FAILED: Got status code {response.status_code}")
                print(f"Response data: {response.data.decode('utf-8')[:500]}...")
                return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ALPHA ELITE STRATEGIC MASTERY TEST")
    print("=" * 60)
    
    success = test_strategic_mastery_function()
    
    if success:
        print("\n🎉 GREAT NEWS! The Alpha Elite strategic mastery is working!")
        print("✨ You should now be able to access the training in your platform")
        print("\n📋 To access it:")
        print("   1. Go to your platform")
        print("   2. Enter Alpha Elite mode")
        print("   3. Click on Strategic Mastery")
        print("   4. Start your training!")
    else:
        print("\n❌ There are still some issues to resolve.")
    
    print("\n" + "=" * 60)
