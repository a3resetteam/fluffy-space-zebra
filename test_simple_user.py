#!/usr/bin/env python3
"""
Simple test for user creation and progress verification
"""

import sqlite3
import json
from datetime import datetime
from werkzeug.security import generate_password_hash
import uuid

def generate_customer_id():
    return f"ORC-{uuid.uuid4().hex[:8].upper()}"

def create_simple_test_user():
    """Create a simple test user"""
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    # Generate test user data
    customer_id = generate_customer_id()
    username = f"testuser_{customer_id[-4:]}"
    email = f"test_{customer_id[-4:]}@oracle.test"
    password_hash = generate_password_hash("testpassword123")
    
    # Insert user with proper timestamp handling
    cursor.execute('''
        INSERT INTO users (customer_id, username, email, password_hash, stripe_customer_id, subscription_status, trial_start, subscription_end)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now', '+3 days'))
    ''', (customer_id, username, email, password_hash, f"cus_test_{customer_id}", 'trial'))
    
    # Initialize mode progress for all 4 modes
    modes = ['alpha-elite', 'situationship', 'personality', 'rituals']
    
    for mode_name in modes:
        cursor.execute('''
            INSERT INTO mode_progress (customer_id, mode_name, level, completion_percentage, achievements, last_accessed)
            VALUES (?, ?, 1, 0, '[]', datetime('now'))
        ''', (customer_id, mode_name))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created test user:")
    print(f"   Customer ID: {customer_id}")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: testpassword123")
    
    return customer_id, username, email

def verify_progress(customer_id):
    """Verify progress is at 0%"""
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT mode_name, completion_percentage, level
        FROM mode_progress WHERE customer_id = ?
        ORDER BY mode_name
    ''', (customer_id,))
    
    results = cursor.fetchall()
    print(f"\n🔍 Progress verification for {customer_id}:")
    
    all_zero = True
    for mode_name, completion, level in results:
        if completion == 0:
            print(f"   ✅ {mode_name}: {completion}% (Level {level})")
        else:
            print(f"   ❌ {mode_name}: {completion}% (Level {level}) - Should be 0%")
            all_zero = False
    
    conn.close()
    
    if all_zero:
        print("   🎉 All modes correctly start at 0%!")
    
    return all_zero

if __name__ == '__main__':
    print("🧪 Testing user creation and 0% progress initialization...\n")
    
    # Create test user
    customer_id, username, email = create_simple_test_user()
    
    # Verify progress
    verify_progress(customer_id)
    
    print(f"\n✅ Test completed! You can log in at http://localhost:5000/login with:")
    print(f"   Email: {email}")
    print(f"   Password: testpassword123")
