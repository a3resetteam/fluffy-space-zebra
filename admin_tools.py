#!/usr/bin/env python3
"""
Admin tools for MYA3Reset: The Oracle
Provides utility functions for managing the payment system and database.
"""

import sqlite3
import sys
from datetime import datetime, timedelta

def migrate_database():
    """Add payment_method_id column if it doesn't exist"""
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN payment_method_id TEXT')
        print("✅ Added payment_method_id column to users table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️  payment_method_id column already exists")
        else:
            print(f"❌ Error adding column: {e}")
    
    conn.commit()
    conn.close()

def list_users():
    """List all users and their subscription status"""
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT customer_id, username, email, subscription_status, trial_start, subscription_end, payment_method_id
        FROM users
        ORDER BY trial_start DESC
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        print("No users found.")
        return
    
    print("\n📋 User List:")
    print("-" * 100)
    print(f"{'Customer ID'[:12]} | {'Username'[:15]} | {'Email'[:25]} | {'Status'[:15]} | {'Trial Start'[:12]} | {'Trial End'[:12]} | {'Payment Method'[:15]}")
    print("-" * 100)
    
    for user in users:
        customer_id, username, email, status, trial_start, trial_end, payment_method = user
        trial_start_short = trial_start[:10] if trial_start else 'N/A'
        trial_end_short = trial_end[:10] if trial_end else 'N/A'
        payment_method_short = 'Yes' if payment_method else 'No'
        
        print(f"{customer_id[:12]} | {username[:15]} | {email[:25]} | {status[:15]} | {trial_start_short[:12]} | {trial_end_short[:12]} | {payment_method_short[:15]}")

def create_test_user():
    """Create a test user for development"""
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    from werkzeug.security import generate_password_hash
    import secrets
    
    # Generate test user data
    customer_id = f"test_{secrets.token_hex(8)}"
    username = f"testuser_{secrets.token_hex(4)}"
    email = f"test_{secrets.token_hex(4)}@example.com"
    password_hash = generate_password_hash("testpass123")
    
    cursor.execute('''
        INSERT INTO users (customer_id, username, email, password_hash, subscription_status, trial_start, subscription_end)
        VALUES (?, ?, ?, ?, 'trial', ?, ?)
    ''', (customer_id, username, email, password_hash, datetime.now(), datetime.now() + timedelta(days=3)))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created test user:")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: testpass123")
    print(f"   Customer ID: {customer_id}")

def simulate_trial_expiry(customer_id):
    """Simulate trial expiry for a user (for testing)"""
    if not customer_id:
        print("❌ Customer ID required")
        return
    
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    # Set trial end to yesterday
    yesterday = datetime.now() - timedelta(days=1)
    
    cursor.execute('''
        UPDATE users 
        SET subscription_end = ?
        WHERE customer_id = ?
    ''', (yesterday, customer_id))
    
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✅ Set trial expiry for customer {customer_id} to {yesterday.strftime('%Y-%m-%d')}")
    else:
        print(f"❌ Customer {customer_id} not found")
    
    conn.close()

def main():
    if len(sys.argv) < 2:
        print("Admin Tools for MYA3Reset: The Oracle")
        print("\nUsage:")
        print("  python admin_tools.py migrate         - Run database migration")
        print("  python admin_tools.py list-users      - List all users")
        print("  python admin_tools.py create-test     - Create test user")
        print("  python admin_tools.py expire-trial <customer_id> - Simulate trial expiry")
        return
    
    command = sys.argv[1]
    
    if command == "migrate":
        migrate_database()
    elif command == "list-users":
        list_users()
    elif command == "create-test":
        create_test_user()
    elif command == "expire-trial":
        if len(sys.argv) < 3:
            print("❌ Customer ID required for expire-trial command")
        else:
            simulate_trial_expiry(sys.argv[2])
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
