#!/usr/bin/env python3
import sqlite3
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect('oracle.db')
cursor = conn.cursor()

# Generate test user data
customer_id = f'ORC-{uuid.uuid4().hex[:8].upper()}'
username = 'testuser'
email = 'test@oracle.com'
password = 'password123'
password_hash = generate_password_hash(password)

# Check if test user already exists
cursor.execute('SELECT id FROM users WHERE email = ? OR username = ?', (email, username))
existing = cursor.fetchone()

if existing:
    print('Test user already exists!')
    cursor.execute('SELECT customer_id, username, email FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    print(f'Customer ID: {user[0]}')
    print(f'Username: {user[1]}')
    print(f'Email: {user[2]}')
else:
    # Create test user
    cursor.execute('''
        INSERT INTO users (customer_id, username, email, password_hash, stripe_customer_id, subscription_status, trial_start, subscription_end)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (customer_id, username, email, password_hash, 'test_stripe_customer', 'trial', datetime.now(), datetime.now() + timedelta(days=3)))
    
    conn.commit()
    print('✅ Test user created successfully!')
    print(f'Customer ID: {customer_id}')
    print(f'Username: {username}')
    print(f'Email: {email}')

print('\n=== TEST LOGIN CREDENTIALS ===')
print('Email: test@oracle.com')
print('Password: password123')
print('===============================')

conn.close()
