#!/usr/bin/env python3
"""
Test complete user flow including registration and progress tracking
"""

import sqlite3
import json
from datetime import datetime
from werkzeug.security import generate_password_hash
import uuid

def generate_customer_id():
    return f"ORC-{uuid.uuid4().hex[:8].upper()}"

def initialize_user_progress(customer_id):
    """Initialize progress tracking for a new user"""
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    # Initialize mode progress for all 4 modes
    modes = [
        ('alpha-elite', 'Alpha Elite Mode'),
        ('situationship', 'Situationship Mode'), 
        ('personality', 'Personality Assessment'),
        ('rituals', 'Custom Ritual Creator')
    ]
    
    for mode_id, mode_name in modes:
        # Check if progress already exists
        cursor.execute('''
            SELECT id FROM mode_progress WHERE customer_id = ? AND mode_name = ?
        ''', (customer_id, mode_id))
        
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO mode_progress (customer_id, mode_name, level, completion_percentage, achievements)
                VALUES (?, ?, 1, 0, '[]')
            ''', (customer_id, mode_id))
    
    conn.commit()
    conn.close()

def create_test_user():
    """Create a test user with proper registration flow"""
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    # Generate test user data
    customer_id = generate_customer_id()
    username = f"testuser_{customer_id[-4:]}"
    email = f"test_{customer_id[-4:]}@oracle.test"
    password_hash = generate_password_hash("testpassword123")
    
    # Insert user
    cursor.execute('''
        INSERT INTO users (customer_id, username, email, password_hash, stripe_customer_id, subscription_status, trial_start, subscription_end)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (customer_id, username, email, password_hash, f"cus_test_{customer_id}", 'trial', datetime.now(), datetime.now()))
    
    # Initialize progress at 0%
    initialize_user_progress(customer_id)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created test user:")
    print(f"   Customer ID: {customer_id}")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: testpassword123")
    
    return customer_id, username, email

def verify_user_progress(customer_id):
    """Verify user progress is correctly initialized"""
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    print(f"\n🔍 Verifying progress for user {customer_id}:")
    
    # Check mode progress
    cursor.execute('''
        SELECT mode_name, completion_percentage, level, achievements
        FROM mode_progress WHERE customer_id = ?
        ORDER BY mode_name
    ''', (customer_id,))
    
    mode_progress = cursor.fetchall()
    all_correct = True
    
    for mode_name, completion, level, achievements in mode_progress:
        if completion == 0 and level == 1:
            print(f"   ✅ {mode_name}: {completion}% (Level {level}) - CORRECT")
        else:
            print(f"   ❌ {mode_name}: {completion}% (Level {level}) - WRONG (should be 0%, Level 1)")
            all_correct = False
    
    # Check user record
    cursor.execute('''
        SELECT transformation_progress FROM users WHERE customer_id = ?
    ''', (customer_id,))
    
    user_record = cursor.fetchone()
    if user_record and user_record[0]:
        try:
            progress_data = json.loads(user_record[0])
            print(f"   📊 User progress data: {progress_data}")
        except:
            print(f"   📊 User progress data: (empty or invalid)")
    else:
        print(f"   📊 User progress data: (empty)")
    
    conn.close()
    
    if all_correct:
        print("   🎉 All progress correctly initialized at 0%!")
    else:
        print("   ⚠️  Some progress values are incorrect")
    
    return all_correct

def simulate_progress_update(customer_id):
    """Simulate a progress update to test the system"""
    from app import update_mode_progress, get_user_progress
    
    print(f"\n🔄 Simulating progress update for user {customer_id}:")
    
    # Update alpha-elite mode to 25%
    new_overall = update_mode_progress(customer_id, 'alpha-elite', 25, ['first_lesson_complete'])
    print(f"   ✅ Updated alpha-elite to 25%, overall progress: {new_overall}%")
    
    # Get current progress
    progress_data = get_user_progress(customer_id)
    print(f"   📊 Current progress: {json.dumps(progress_data, indent=4)}")
    
    return progress_data

if __name__ == '__main__':
    print("🧪 Testing complete user registration and progress flow...\n")
    
    # Create test user
    customer_id, username, email = create_test_user()
    
    # Verify initial progress
    verify_user_progress(customer_id)
    
    # Test progress update
    simulate_progress_update(customer_id)
    
    print(f"\n✅ Test completed! You can now log in with:")
    print(f"   Email: {email}")
    print(f"   Password: testpassword123")
    print(f"   Customer ID: {customer_id}")
