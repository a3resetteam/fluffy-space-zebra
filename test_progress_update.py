#!/usr/bin/env python3
"""
Test progress updates and dashboard integration
"""

import sqlite3
import json
import requests
import time

def test_progress_update():
    """Test progress updating for an existing user"""
    # Get the most recent test user
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT customer_id, email FROM users 
        WHERE email LIKE 'test_%@oracle.test' 
        ORDER BY id DESC LIMIT 1
    ''')
    
    user = cursor.fetchone()
    if not user:
        print("❌ No test user found. Please run test_simple_user.py first.")
        return
    
    customer_id, email = user
    print(f"🧪 Testing progress updates for user: {customer_id}")
    
    # Check initial progress
    cursor.execute('''
        SELECT mode_name, completion_percentage FROM mode_progress 
        WHERE customer_id = ? ORDER BY mode_name
    ''', (customer_id,))
    
    initial_progress = cursor.fetchall()
    print(f"📊 Initial progress:")
    for mode_name, completion in initial_progress:
        print(f"   {mode_name}: {completion}%")
    
    # Update progress for alpha-elite mode
    cursor.execute('''
        UPDATE mode_progress 
        SET completion_percentage = 35, last_accessed = datetime('now')
        WHERE customer_id = ? AND mode_name = 'alpha-elite'
    ''', (customer_id,))
    
    # Update progress for situationship mode  
    cursor.execute('''
        UPDATE mode_progress 
        SET completion_percentage = 20, last_accessed = datetime('now')
        WHERE customer_id = ? AND mode_name = 'situationship'
    ''', (customer_id,))
    
    conn.commit()
    
    # Check updated progress
    cursor.execute('''
        SELECT mode_name, completion_percentage FROM mode_progress 
        WHERE customer_id = ? ORDER BY mode_name
    ''', (customer_id,))
    
    updated_progress = cursor.fetchall()
    print(f"\n📈 Updated progress:")
    total_progress = 0
    for mode_name, completion in updated_progress:
        print(f"   {mode_name}: {completion}%")
        total_progress += completion
    
    overall_progress = total_progress / 4
    print(f"\n🎯 Overall progress should be: {overall_progress}%")
    
    conn.close()
    
    print(f"\n✅ Test completed!")
    print(f"📝 You can now log in at http://localhost:5000/login with:")
    print(f"   Email: {email}")
    print(f"   Password: testpassword123")
    print(f"   The dashboard should show the updated progress values!")

if __name__ == '__main__':
    test_progress_update()
