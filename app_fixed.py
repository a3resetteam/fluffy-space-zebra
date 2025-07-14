#!/usr/bin/env python3
"""
MYA3Reset: The Oracle - FIXED VERSION FOR IMMEDIATE LAUNCH
"""

import os
import sqlite3
import json
import secrets
import uuid
import datetime as dt
from datetime import datetime, timedelta
from flask import Flask, request, render_template_string, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'oracle_secret_key_2024')

# Simple database initialization
def init_db():
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    # Users table
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
    
    # User progress tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            mode_name TEXT NOT NULL,
            completion_percentage INTEGER DEFAULT 0,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Shadow work responses
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

# Templates
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MYA3Reset: The Oracle</title>
    <style>
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #000000 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            color: #ffffff;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 50px;
            padding: 40px 0;
        }
        .header h1 {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #ffffff 0%, #74b9ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .card {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid #333;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }
        .form-group {
            margin-bottom: 25px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #ffffff;
        }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #333;
            border-radius: 12px;
            font-size: 16px;
            background: #1a1a2e;
            color: #ffffff;
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
        }
        .modes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }
        .mode-card {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 2px solid #333;
            border-radius: 20px;
            padding: 35px;
            text-align: center;
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
        {% if session.customer_id %}
        <div style="background: #1a1a2e; padding: 20px; border-radius: 15px; margin-bottom: 30px;">
            <strong>🔮 Welcome back, {{ session.username }}!</strong>
            <a href="{{ url_for('logout') }}" class="btn">🚪 Logout</a>
        </div>
        {% endif %}
        
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

# Routes
@app.route('/')
def home():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    content = '''
    <div class="header">
        <h1>MYA3Reset: The Oracle</h1>
        <p>🔮 Transform Your Reality • Unlock Your Potential • Master Your Destiny</p>
    </div>
    
    <div class="modes-grid">
        <div class="mode-card">
            <h3>👑 Alpha Elite Mode</h3>
            <p>Develop unshakeable confidence and leadership presence.</p>
            <a href="{{ url_for('alpha_elite') }}" class="btn">🚀 Enter Alpha Mode</a>
        </div>
        
        <div class="mode-card">
            <h3>💝 Situationship Mode</h3>
            <p>Navigate modern relationships and set boundaries.</p>
            <a href="{{ url_for('situationship') }}" class="btn">💎 Master Relationships</a>
        </div>
        
        <div class="mode-card">
            <h3>🌑 Shadow Work</h3>
            <p>30 deep prompts to uncover your hidden patterns.</p>
            <a href="{{ url_for('shadow_work') }}" class="btn">🌑 Begin Journey</a>
        </div>
        
        <div class="mode-card">
            <h3>⚡ Custom Rituals</h3>
            <p>Design personalized daily transformation rituals.</p>
            <a href="{{ url_for('rituals') }}" class="btn">🛠️ Create Rituals</a>
        </div>
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
        
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE email = ? OR username = ?', (email, username))
        if cursor.fetchone():
            flash('User already exists')
            conn.close()
            return redirect(url_for('register'))
        
        # Create user
        customer_id = generate_customer_id()
        password_hash = generate_password_hash(password)
        
        cursor.execute('''
            INSERT INTO users (customer_id, username, email, password_hash)
            VALUES (?, ?, ?, ?)
        ''', (customer_id, username, email, password_hash))
        
        conn.commit()
        conn.close()
        
        # Log in user
        session['customer_id'] = customer_id
        session['username'] = username
        
        flash('Registration successful! Welcome to The Oracle.')
        return redirect(url_for('home'))
    
    content = '''
    <div class="header">
        <h1>MYA3Reset: The Oracle</h1>
        <p>🌟 Begin Your Elite Transformation</p>
    </div>
    
    <div class="card">
        <h2 style="text-align: center; margin-bottom: 30px;">Join The Elite Circle 🔮</h2>
        <form method="POST">
            <div class="form-group">
                <label for="username">👤 Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="email">📧 Email Address:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">🔐 Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div style="text-align: center;">
                <button type="submit" class="btn">🎯 START FREE TRIAL</button>
            </div>
        </form>
        <div style="text-align: center; margin-top: 30px;">
            Already have an account? <a href="{{ url_for('login') }}" style="color: #74b9ff;">🔐 Login Here</a>
        </div>
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
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="font-size: 3rem; color: #ffffff; margin-bottom: 15px;">🔮 MYA3Reset: The Oracle</h1>
        <p style="font-size: 1.3rem; color: #ffffff; font-weight: 500;">Your Ritual, Your Transformation, Your Alchemy</p>
    </div>

    <!-- Login Form -->
    <div class="card" style="margin-bottom: 40px;">
        <h2 style="text-align: center; margin-bottom: 25px; color: #ffffff;">Welcome Back, Elite 👑</h2>
        <form method="POST">
            <div class="form-group">
                <label for="email">📧 Email Address:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">🔑 Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div style="text-align: center;">
                <button type="submit" class="btn">🚀 ENTER THE ORACLE</button>
            </div>
        </form>
        <div style="text-align: center; margin-top: 25px;">
            New to the Oracle? 
            <a href="{{ url_for('register') }}" style="color: #74b9ff; text-decoration: none; font-weight: 600;">✨ Start Your 3-Day Free Trial</a>
        </div>
        <div style="background: rgba(116, 185, 255, 0.1); border: 2px solid #74b9ff; padding: 15px; border-radius: 10px; margin-top: 20px; text-align: center;">
            <p style="margin: 0; color: #74b9ff; font-size: 16px;">🎁 <strong>3 Days Free</strong> • Then $19.99/month • Cancel Anytime</p>
        </div>
    </div>

    <!-- What The Oracle Offers -->
    <div style="background: #1a1a2e; border: 2px solid #333333; border-radius: 20px; padding: 30px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(255, 255, 255, 0.05);">
        <h2 style="text-align: center; color: #ffffff; margin-bottom: 30px;">🔮 The 4 Transformation Modes Inside The Oracle</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 30px;">
            <div style="background: #1a1a2e; border: 2px solid #74b9ff; border-radius: 15px; padding: 25px; text-align: center; transition: all 0.3s ease;">
                <h3 style="color: #74b9ff; margin-bottom: 15px; font-size: 1.4rem;">👑 Alpha Elite Mode</h3>
                <p style="color: #ffffff; font-size: 1rem; margin: 0; line-height: 1.6;">Master executive presence, strategic decision-making, and high-performance leadership. Develop the mindset, communication skills, and emotional intelligence that separates industry leaders from the competition.</p>
            </div>
            <div style="background: #1a1a2e; border: 2px solid #fd79a8; border-radius: 15px; padding: 25px; text-align: center; transition: all 0.3s ease;">
                <h3 style="color: #fd79a8; margin-bottom: 15px; font-size: 1.4rem;">💝 Situationship Mode</h3>
                <p style="color: #ffffff; font-size: 1rem; margin: 0; line-height: 1.6;">Navigate complex modern relationships with clarity and confidence. Master boundary setting, emotional intelligence, and authentic communication to attract and maintain meaningful connections that align with your values.</p>
            </div>
            <div style="background: #1a1a2e; border: 2px solid #00b894; border-radius: 15px; padding: 25px; text-align: center; transition: all 0.3s ease;">
                <h3 style="color: #00b894; margin-bottom: 15px; font-size: 1.4rem;">🧠 A3Reset Assessment Mode</h3>
                <p style="color: #ffffff; font-size: 1rem; margin: 0; line-height: 1.6;">Comprehensive psychological profiling and transformation readiness evaluation. Discover your unique personality matrix, identify limiting patterns, and receive personalized strategies for accelerated personal development.</p>
            </div>
            <div style="background: #1a1a2e; border: 2px solid #e17055; border-radius: 15px; padding: 25px; text-align: center; transition: all 0.3s ease;">
                <h3 style="color: #e17055; margin-bottom: 15px; font-size: 1.4rem;">🎭 Custom Ritual Creator</h3>
                <p style="color: #ffffff; font-size: 1rem; margin: 0; line-height: 1.6;">Design bespoke transformation protocols tailored to your specific goals and lifestyle. Create powerful daily practices, mindset anchors, and behavioral systems that compound into lasting change.</p>
            </div>
        </div>
        
        <!-- Exclusive Features -->
        <div style="background: rgba(116, 185, 255, 0.1); border: 2px solid #74b9ff; border-radius: 15px; padding: 25px; text-align: center;">
            <h3 style="color: #74b9ff; margin-bottom: 20px; font-size: 1.3rem;">⚡ Plus Exclusive Oracle Features</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px;">
                <div>
                    <h4 style="color: #00ff88; margin-bottom: 8px; font-size: 1.1rem;">🤖 AI Coach</h4>
                    <p style="color: #ffffff; font-size: 0.9rem; margin: 0;">Multiple AI personalities for personalized guidance</p>
                </div>
                <div>
                    <h4 style="color: #fd79a8; margin-bottom: 8px; font-size: 1.1rem;">📊 Progress Tracking</h4>
                    <p style="color: #ffffff; font-size: 0.9rem; margin: 0;">Advanced analytics to monitor your transformation</p>
                </div>
                <div>
                    <h4 style="color: #e17055; margin-bottom: 8px; font-size: 1.1rem;">🎯 Daily Challenges</h4>
                    <p style="color: #ffffff; font-size: 0.9rem; margin: 0;">Gamified experiences for consistent growth</p>
                </div>
                <div>
                    <h4 style="color: #74b9ff; margin-bottom: 8px; font-size: 1.1rem;">🌑 Shadow Work</h4>
                    <p style="color: #ffffff; font-size: 0.9rem; margin: 0;">Deep psychological integration and healing</p>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE.replace('{{ content }}', content))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/shadow-work', methods=['GET', 'POST'])
def shadow_work():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    shadow_prompts = [
        "What patterns do you notice in your relationships that you'd like to change?",
        "When do you feel most insecure in relationships? What triggers this feeling?",
        "What do you fear most about being vulnerable with someone?",
        "How do you typically react when someone doesn't respond to your messages?",
        "What beliefs about love did you learn from your family growing up?"
    ]
    
    prompt_number = int(request.args.get('prompt', 1))
    if prompt_number > len(shadow_prompts):
        prompt_number = 1
    
    current_prompt = shadow_prompts[prompt_number - 1]
    
    if request.method == 'POST':
        response = request.form.get('response', '').strip()
        if response:
            conn = sqlite3.connect('oracle.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO shadow_work_responses (customer_id, prompt_id, response)
                VALUES (?, ?, ?)
            ''', (session['customer_id'], prompt_number - 1, response))
            conn.commit()
            conn.close()
            
            flash('Shadow work response saved! 🌑 Deep insights recorded.')
            next_prompt = prompt_number + 1 if prompt_number < len(shadow_prompts) else 1
            return redirect(url_for('shadow_work', prompt=next_prompt))
    
    content = f'''
    <div class="header">
        <h1>🌑 Shadow Work</h1>
        <p>Deep Self-Discovery Journey</p>
    </div>
    
    <div class="card">
        <h3>Prompt {prompt_number} of {len(shadow_prompts)}</h3>
        <p style="font-size: 1.2rem; margin: 20px 0;">{current_prompt}</p>
        
        <form method="POST">
            <div class="form-group">
                <label for="response">Your Response:</label>
                <textarea id="response" name="response" rows="6" placeholder="Share your thoughts honestly..."></textarea>
            </div>
            <div style="text-align: center;">
                <button type="submit" class="btn">💫 Save Response</button>
            </div>
        </form>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE.replace('{{ content }}', content))

@app.route('/alpha-elite')
def alpha_elite():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    content = '''
    <div class="header">
        <h1>👑 Alpha Elite Mode</h1>
        <p>Develop Unshakeable Confidence & Leadership</p>
    </div>
    
    <div class="card">
        <h3>🚀 Coming Soon</h3>
        <p>Alpha Elite features are being finalized for launch. You'll have access to:</p>
        <ul style="margin: 20px 0;">
            <li>Leadership development exercises</li>
            <li>Confidence building challenges</li>
            <li>Strategic thinking workshops</li>
            <li>Performance optimization tools</li>
        </ul>
        <a href="{{ url_for('home') }}" class="btn">🏠 Back to Dashboard</a>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE.replace('{{ content }}', content))

@app.route('/situationship')
def situationship():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    content = '''
    <div class="header">
        <h1>💝 Situationship Mode</h1>
        <p>Master Modern Relationships & Dating</p>
    </div>
    
    <div class="modes-grid">
        <div class="mode-card">
            <h3>🌑 Shadow Work</h3>
            <p>Uncover your relationship patterns</p>
            <a href="{{ url_for('shadow_work') }}" class="btn">Begin Journey</a>
        </div>
        
        <div class="mode-card">
            <h3>🛡️ Boundary Setting</h3>
            <p>Learn to set healthy boundaries</p>
            <a href="{{ url_for('home') }}" class="btn">Coming Soon</a>
        </div>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE.replace('{{ content }}', content))

@app.route('/rituals')
def rituals():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    content = '''
    <div class="header">
        <h1>⚡ Custom Ritual Creator</h1>
        <p>Design Your Personalized Daily Rituals</p>
    </div>
    
    <div class="card">
        <h3>🛠️ Coming Soon</h3>
        <p>Custom ritual features are being finalized. You'll be able to create personalized transformation rituals.</p>
        <a href="{{ url_for('home') }}" class="btn">🏠 Back to Dashboard</a>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE.replace('{{ content }}', content))

if __name__ == '__main__':
    init_db()
    print("🚀 Oracle Platform FIXED VERSION starting on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
