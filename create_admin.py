#!/usr/bin/env python3
"""
Create CEO admin account for Oracle admin panel
"""
import sqlite3
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

def create_admin():
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    # Add is_admin column if it doesn't exist
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE')
        print("Added is_admin column to users table")
    except sqlite3.OperationalError:
        print("is_admin column already exists")
    
    # CEO credentials
    email = 'marlexus@a3reset.com'
    password = 'A3password123'
    customer_id = str(uuid.uuid4())
    
    # Create admin user
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (customer_id, username, email, password_hash, subscription_status, created_at, is_admin)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (customer_id, 'CEO', email, generate_password_hash(password), 'admin', datetime.now(), True))
    
    conn.commit()
    conn.close()
    
    print('✅ CEO Admin Account Created Successfully!')
    print(f'📧 Email: {email}')
    print(f'🔑 Password: {password}')
    print('🔗 Access admin panel at: /admin')
    print('🎯 Login at: /login (then navigate to /admin)')

if __name__ == "__main__":
    create_admin()
