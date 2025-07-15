#!/usr/bin/env python3
"""
MYA3Reset: The Oracle - CLEAN VERSION
"""

import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, render_template_string, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'oracle_secret_key_2024')

def init_db():
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            subscription_status TEXT DEFAULT 'trial',
            trial_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT FALSE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shadow_work_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            prompt_id INTEGER NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def generate_customer_id():
    return f"ORC-{uuid.uuid4().hex[:8].upper()}"

# Initialize database
init_db()

# Template
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MYA3Reset: The Oracle</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #000000;
            min-height: 100vh;
            color: #ffffff;
            margin: 0;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .card {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            border: 2px solid #404040;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.8);
        }
        .form-group { margin-bottom: 25px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 500; }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #404040;
            border-radius: 12px;
            font-size: 16px;
            background: #1a1a1a;
            color: #ffffff;
            box-sizing: border-box;
        }
        .btn {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: #ffffff;
            padding: 15px 35px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 8px;
            font-weight: 600;
        }
        .flash-message {
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
            color: #ffffff;
        }
    </style>
</head>
<body>
    <div class="container">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="flash-message">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {{ content }}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    content = f'''
    <div class="card">
        <h1>🔮 Welcome to The Oracle</h1>
        <p>Welcome back, {session.get('username', 'User')}!</p>
        <a href="{{ url_for('logout') }}" class="btn">Logout</a>
    </div>
    
    <div class="card">
        <h2>🚀 Your Transformation Modes</h2>
        <p>👑 Alpha Elite Mode - Coming Soon</p>
        <p>💝 Situationship Mode - Coming Soon</p>
        <p>🌑 Shadow Work - <a href="{{ url_for('shadow_work') }}" class="btn">Start</a></p>
        <p>⚡ Custom Rituals - Coming Soon</p>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE.replace('{{ content }}', content))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('oracle.db')
        cursor = conn.cursor()
        
        try:
            customer_id = generate_customer_id()
            password_hash = generate_password_hash(password)
            
            cursor.execute('''
                INSERT INTO users (customer_id, username, email, password_hash)
                VALUES (?, ?, ?, ?)
            ''', (customer_id, username, email, password_hash))
            
            conn.commit()
            session['customer_id'] = customer_id
            session['username'] = username
            flash('Registration successful! Welcome to The Oracle.')
            return redirect(url_for('home'))
        except:
            flash('Username or email already exists')
        finally:
            conn.close()
    
    content = '''
    <div class="card">
        <h1>🔮 Join The Oracle</h1>
        <form method="POST">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Join Oracle</button>
        </form>
        <p><a href="{{ url_for('login') }}" style="color: #74b9ff;">Already have account? Login</a></p>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE.replace('{{ content }}', content))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('oracle.db')
        cursor = conn.cursor()
        cursor.execute('SELECT customer_id, username, password_hash FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['customer_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('home'))
        
        flash('Invalid email or password')
    
    content = '''
    <div class="card">
        <h1>🔮 Oracle Login</h1>
        <form method="POST">
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
        <p><a href="{{ url_for('register') }}" style="color: #74b9ff;">New user? Register</a></p>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE.replace('{{ content }}', content))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/shadow-work')
def shadow_work():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    content = '''
    <div class="card">
        <h1>🌑 Shadow Work</h1>
        <p>Deep self-discovery journey coming soon!</p>
        <a href="{{ url_for('home') }}" class="btn">Back to Dashboard</a>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE.replace('{{ content }}', content))

# NO if __name__ == '__main__' block - let Gunicorn handle it

web: gunicorn app:app --bind 0.0.0.0:$PORT

