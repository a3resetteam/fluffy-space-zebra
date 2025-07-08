#!/usr/bin/env python3
"""
Test script for progress tracking functionality
"""

import sqlite3
import json
from datetime import datetime
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
    print(f"Initialized progress for user {customer_id}")

def get_user_progress(customer_id):
    """Get comprehensive user progress data"""
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    # Get mode progress
    cursor.execute('''
        SELECT mode_name, completion_percentage, level, achievements, last_accessed
        FROM mode_progress WHERE customer_id = ?
    ''', (customer_id,))
    mode_data = cursor.fetchall()
    
    # Get total sessions
    cursor.execute('''
        SELECT COUNT(*) FROM user_sessions WHERE customer_id = ?
    ''', (customer_id,))
    total_sessions = cursor.fetchone()[0] or 0
    
    # Get user progress data
    cursor.execute('''
        SELECT transformation_progress FROM users WHERE customer_id = ?
    ''', (customer_id,))
    user_progress = cursor.fetchone()
    
    conn.close()
    
    if user_progress and user_progress[0]:
        try:
            progress_data = json.loads(user_progress[0])
        except:
            progress_data = {'overall_progress': 0, 'modes': {}}
    else:
        progress_data = {'overall_progress': 0, 'modes': {}}
    
    # Calculate current progress from mode_progress table
    mode_progress = {}
    total_progress = 0
    for mode_name, completion, level, achievements, last_accessed in mode_data:
        mode_progress[mode_name] = {
            'completion_percentage': completion,
            'level': level,
            'achievements': json.loads(achievements or '[]'),
            'last_accessed': last_accessed
        }
        total_progress += completion
    
    # Calculate overall progress (average of all modes)
    overall_progress = total_progress / 4 if mode_data else 0
    
    return {
        'overall_progress': round(overall_progress, 1),
        'modes': mode_progress,
        'total_sessions': total_sessions,
        'user_data': progress_data
    }

def test_progress_tracking():
    """Test the progress tracking system"""
    print("Testing progress tracking system...")
    
    # Create test user
    test_customer_id = generate_customer_id()
    print(f"Test customer ID: {test_customer_id}")
    
    # Initialize progress
    initialize_user_progress(test_customer_id)
    
    # Get initial progress
    initial_progress = get_user_progress(test_customer_id)
    print("Initial progress:")
    print(json.dumps(initial_progress, indent=2))
    
    # Verify all modes start at 0%
    for mode_name, mode_data in initial_progress['modes'].items():
        if mode_data['completion_percentage'] != 0:
            print(f"ERROR: {mode_name} should start at 0%, but is {mode_data['completion_percentage']}%")
            return False
        else:
            print(f"✓ {mode_name}: 0% (correct)")
    
    if initial_progress['overall_progress'] != 0:
        print(f"ERROR: Overall progress should be 0%, but is {initial_progress['overall_progress']}%")
        return False
    else:
        print("✓ Overall progress: 0% (correct)")
    
    print("✅ Progress tracking test passed!")
    return True

if __name__ == '__main__':
    test_progress_tracking()
