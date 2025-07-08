#!/usr/bin/env python3
"""
MYA3Reset: The Oracle - Premium Transformation Platform
A comprehensive web application with Stripe integration and 4 specialized modes
"""

import os
import sqlite3
import stripe
import json
import random
import secrets
import uuid
from datetime import datetime, timedelta, date
from flask import Flask, request, render_template, render_template_string, redirect, url_for, session, flash, jsonify, send_from_directory, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_stripe_secret_key')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_your_stripe_publishable_key')
STRIPE_PRODUCT_ID = 'prod_SZVuyI8OkJaIQa'
STRIPE_PRICE_ID = os.environ.get('STRIPE_PRICE_ID', 'price_1999_monthly')  # $19.99/month price ID

# Database setup
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
            stripe_customer_id TEXT,
            payment_method_id TEXT,
            subscription_status TEXT DEFAULT 'trial',
            trial_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            subscription_end TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            profile_data TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            transformation_progress TEXT DEFAULT '{}'
        )
    ''')
    
    # User sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            mode TEXT NOT NULL,
            session_data TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            progress INTEGER DEFAULT 0
        )
    ''')
    
    # Mode progress
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mode_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            mode_name TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            completion_percentage INTEGER DEFAULT 0,
            achievements TEXT DEFAULT '[]',
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Daily challenges
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            challenge_date DATE NOT NULL,
            mode TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            points INTEGER DEFAULT 10
        )
    ''')
    
    # Situationship Mode tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            date DATE NOT NULL,
            mood TEXT NOT NULL,
            notes TEXT,
            UNIQUE(customer_id, date)
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            personality TEXT NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add payment_method_id column if it doesn't exist (migration)
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN payment_method_id TEXT')
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    conn.commit()
    conn.close()

def generate_customer_id():
    return f"ORC-{uuid.uuid4().hex[:8].upper()}"

def check_subscription_status(customer_id):
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT subscription_status, trial_start, subscription_end 
        FROM users WHERE customer_id = ?
    ''', (customer_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return False
    
    status, trial_start, subscription_end = result
    now = datetime.now()
    
    # Check trial period (3 days)
    if status == 'trial':
        if isinstance(trial_start, str):
            trial_start_dt = datetime.fromisoformat(trial_start.replace('Z', '+00:00'))
        else:
            trial_start_dt = trial_start
        if (now - trial_start_dt).days < 3:
            return True
    
    # Check active subscription
    if status == 'active' and subscription_end:
        if isinstance(subscription_end, str):
            sub_end_dt = datetime.fromisoformat(subscription_end.replace('Z', '+00:00'))
        else:
            sub_end_dt = subscription_end
        if now < sub_end_dt:
            return True
    
    return False

# HTML Templates
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MYA3Reset: The Oracle</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #000000 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            color: #ffffff;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
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
            background-clip: text;
            text-shadow: 0 0 30px rgba(255,255,255,0.3);
        }
        
        .header p {
            font-size: 1.3rem;
            color: #c0c0c0;
            font-weight: 300;
        }
        
        .card {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid #333;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 30px 60px rgba(116, 185, 255, 0.2);
            border-color: #74b9ff;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #ffffff;
            font-size: 1.1rem;
        }
        
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #333;
            border-radius: 12px;
            font-size: 16px;
            background: #1a1a2e;
            color: #ffffff;
            transition: all 0.3s ease;
        }
        
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: #74b9ff;
            box-shadow: 0 0 20px rgba(116, 185, 255, 0.3);
        }
        
        .btn {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: #ffffff;
            padding: 15px 35px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(116, 185, 255, 0.4);
            background: linear-gradient(135deg, #0984e3 0%, #74b9ff 100%);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #636e72 0%, #2d3436 100%);
            color: #ffffff;
        }
        
        .btn-success {
            background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
            color: #ffffff;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #e17055 0%, #fd79a8 100%);
            color: #ffffff;
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
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }
        
        .mode-card:hover {
            border-color: #74b9ff;
            transform: scale(1.02);
            box-shadow: 0 20px 40px rgba(116, 185, 255, 0.3);
        }
        
        .mode-card h3 {
            color: #ffffff;
            margin-bottom: 20px;
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        .mode-card p {
            margin-bottom: 25px;
            color: #c0c0c0;
            font-size: 1.1rem;
        }
        
        .progress-bar {
            background: #333;
            border-radius: 15px;
            height: 8px;
            margin: 20px 0;
            overflow: hidden;
        }
        
        .progress-fill {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            height: 100%;
            transition: width 0.6s ease;
            border-radius: 15px;
        }
        
        .user-info {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid #333;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            color: #ffffff;
        }
        
        .flash-messages {
            margin-bottom: 30px;
        }
        
        .flash-message {
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 15px;
            font-weight: 500;
            background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
            color: #ffffff;
        }
        
        .flash-error {
            background: linear-gradient(135deg, #e17055 0%, #fd79a8 100%);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #2d3436 0%, #636e72 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #74b9ff;
        }
        
        .stat-label {
            color: #c0c0c0;
            margin-top: 5px;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            .header h1 {
                font-size: 2.5rem;
            }
            
            .modes-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if session.customer_id %}
        <div class="user-info">
            <strong>🔮 Welcome back, {{ session.username }}!</strong><br>
            <span style="color: #c0c0c0;">Customer ID: {{ session.customer_id }}</span>
            {% if session.is_admin %}
                <span style="color: #00ff88; margin-left: 15px;">👑 ADMIN</span>
            {% endif %}
            <div style="margin-top: 15px;">
                <a href="{{ url_for('profile') }}" class="btn btn-secondary">👤 Profile</a>
                {% if session.is_admin %}
                    <a href="{{ url_for('admin') }}" class="btn btn-success">⚙️ Admin Panel</a>
                {% endif %}
                <a href="{{ url_for('logout') }}" class="btn btn-danger">🚪 Logout</a>
            </div>
        </div>
        {% endif %}
        
        <div class="flash-messages">
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="flash-message">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
        </div>
        
        {{ content }}
    </div>
</body>
</html>
'''

HOME_TEMPLATE = '''
<div class="header">
    <h1>MYA3Reset: The Oracle</h1>
    <p>🔮 Transform Your Reality • Unlock Your Potential • Master Your Destiny</p>
</div>

<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">{{ days_active }}</div>
        <div class="stat-label">Days Active</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{{ sessions_completed }}</div>
        <div class="stat-label">Sessions</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{{ overall_progress }}%</div>
        <div class="stat-label">Progress</div>
    </div>
</div>

<div class="modes-grid">
    <div class="mode-card">
        <h3>👑 Alpha Elite Mode</h3>
        <p>Develop unshakeable confidence, leadership presence, and elite-level performance mindsets.</p>
        <div class="progress-bar">
            <div class="progress-fill" style="width: 25%"></div>
        </div>
        <p style="margin-top: 15px; color: #74b9ff;">Progress: 25%</p>
        <a href="{{ url_for('mode_page', mode_name='alpha-elite') }}" class="btn">🚀 Enter Alpha Mode</a>
    </div>
    
    <div class="mode-card">
        <h3>💝 Situationship Mode</h3>
        <p>Navigate modern relationships, set boundaries, and attract high-value connections.</p>
        <div class="progress-bar">
            <div class="progress-fill" style="width: 15%"></div>
        </div>
        <p style="margin-top: 15px; color: #74b9ff;">Progress: 15%</p>
        <a href="{{ url_for('situationship_mode') }}" class="btn">💎 Master Relationships</a>
    </div>
    
    <div class="mode-card">
        <h3>🧠 Personality Assessment</h3>
        <p>Deep psychological profiling to understand your core traits and transformation areas.</p>
        <div class="progress-bar">
            <div class="progress-fill" style="width: 10%"></div>
        </div>
        <p style="margin-top: 15px; color: #74b9ff;">Progress: 10%</p>
        <a href="{{ url_for('mode_page', mode_name='personality') }}" class="btn">🔍 Discover Yourself</a>
    </div>
    
    <div class="mode-card">
        <h3>⚡ Custom Ritual Creator</h3>
        <p>Design personalized daily rituals and habits that align with your transformation goals.</p>
        <div class="progress-bar">
            <div class="progress-fill" style="width: 5%"></div>
        </div>
        <p style="margin-top: 15px; color: #74b9ff;">Progress: 5%</p>
        <a href="{{ url_for('mode_page', mode_name='rituals') }}" class="btn">🛠️ Create Rituals</a>
    </div>
</div>
'''

LOGIN_TEMPLATE = '''
<div class="header">
    <h1>MYA3Reset: The Oracle</h1>
    <p>🔐 Access Your Transformation Portal</p>
</div>

<div class="card">
    <h2 style="text-align: center; margin-bottom: 30px; color: #ffffff;">Welcome Back, Elite 👑</h2>
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
    <div style="text-align: center; margin-top: 30px; color: #c0c0c0;">
        New to the Oracle? <a href="{{ url_for('register') }}" style="color: #74b9ff; text-decoration: none;">✨ Start Your Journey</a>
    </div>
</div>
'''

REGISTER_TEMPLATE = '''
<div class="header">
    <h1>MYA3Reset: The Oracle</h1>
    <p>🌟 Begin Your Elite Transformation</p>
</div>

<div class="card">
    <h2 style="text-align: center; margin-bottom: 20px; color: #ffffff;">Join The Elite Circle 🔮</h2>
    <p style="text-align: center; color: #c0c0c0; margin-bottom: 30px;">
        ✨ 3-Day Free Trial • Then $19.99/month<br>
        🚀 Unlock all 4 transformation modes
    </p>
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
        <div class="form-group">
            <label for="confirm_password">🔒 Confirm Password:</label>
            <input type="password" id="confirm_password" name="confirm_password" required>
        </div>
        <div style="text-align: center;">
            <button type="submit" class="btn">🎯 START FREE TRIAL</button>
        </div>
    </form>
    <div style="text-align: center; margin-top: 30px; color: #c0c0c0;">
        Already have an account? <a href="{{ url_for('login') }}" style="color: #74b9ff; text-decoration: none;">🔐 Login Here</a>
    </div>
</div>
'''

SITUATIONSHIP_TEMPLATE = '''
<div class="header">
    <h1>💝 Situationship Mode</h1>
    <p>Master Modern Relationships & Dating</p>
</div>

<div class="modes-grid">
    <div class="mode-card">
        <h3>📊 Mood Tracker</h3>
        <p>Track your emotional journey and get personalized insights</p>
        <a href="{{ url_for('mood_tracker') }}" class="btn">Start Tracking</a>
    </div>
    
    <div class="mode-card">
        <h3>🌑 Shadow Work</h3>
        <p>30 deep prompts to uncover your hidden patterns</p>
        <a href="{{ url_for('shadow_work') }}" class="btn">Begin Journey</a>
    </div>
    
    <div class="mode-card">
        <h3>🎯 Decision Game</h3>
        <p>Practice making better relationship choices</p>
        <a href="{{ url_for('decision_game') }}" class="btn">Play Game</a>
    </div>
    
    <div class="mode-card">
        <h3>🛡️ Boundary Setting</h3>
        <p>Learn to set and maintain healthy boundaries</p>
        <a href="{{ url_for('boundary_setting') }}" class="btn">Set Boundaries</a>
    </div>
    
    <div class="mode-card">
        <h3>🤖 AI Coach</h3>
        <p>Get personalized advice from 4 coaching personalities</p>
        <a href="{{ url_for('ai_coach') }}" class="btn">Get Coaching</a>
    </div>
    
    <div class="mode-card">
        <h3>💎 Worth Assessment</h3>
        <p>Evaluate your self-worth across multiple domains</p>
        <a href="{{ url_for('worth_assessment') }}" class="btn">Take Assessment</a>
    </div>
</div>
'''

RITUAL_CREATOR_TEMPLATE = '''
<div class="header">
    <h1>⚡ Custom Ritual Creator</h1>
    <p>Design Your Personalized Daily Rituals</p>
</div>

<div class="card">
    <h2 style="text-align: center; margin-bottom: 20px; color: #ffffff;">Create Your Ritual 🔮</h2>
    <form method="POST" action="{{ url_for('ritual_session') }}">
        <div class="form-group">
            <label for="birthday">🎂 Your Birthday:</label>
            <input type="date" id="birthday" name="birthday">
        </div>
        <div class="form-group">
            <label for="mood">😊 Current Mood:</label>
            <select id="mood" name="mood">
                <option value="calm">Calm</option>
                <option value="energized">Energized</option>
                <option value="stressed">Stressed</option>
                <option value="tired">Tired</option>
                <option value="anxious">Anxious</option>
                <option value="excited">Excited</option>
            </select>
        </div>
        <div class="form-group">
            <label for="environment">🏡 Environment:</label>
            <select id="environment" name="environment">
                <option value="indoor">Indoor</option>
                <option value="outdoor">Outdoor</option>
                <option value="office">Office</option>
                <option value="gym">Gym</option>
            </select>
        </div>
        <div class="form-group">
            <label for="time_of_day">🕒 Time of Day:</label>
            <select id="time_of_day" name="time_of_day">
                <option value="morning">Morning</option>
                <option value="afternoon">Afternoon</option>
                <option value="evening">Evening</option>
            </select>
        </div>
        <div class="form-group">
            <label for="duration">⏳ Duration (minutes):</label>
            <input type="number" id="duration" name="duration" value="15" min="5" max="60">
        </div>
        <div class="form-group">
            <label for="ritual_need">✨ Ritual Focus:</label>
            <select id="ritual_need" name="ritual_need">
                <option value="energy">Energy</option>
                <option value="grounding">Grounding</option>
                <option value="peace">Inner Peace</option>
                <option value="clarity">Mental Clarity</option>
                <option value="confidence">Confidence</option>
                <option value="healing">Emotional Healing</option>
            </select>
        </div>
        <div style="text-align: center;">
            <button type="submit" class="btn">🎉 Create Ritual Session</button>
        </div>
    </form>
</div>
'''

RITUAL_SESSION_TEMPLATE = '''
<div class="header">
    <h1>🧘‍♀️ Your Ritual Session</h1>
    <p>Personalized Ritual in Progress...</p>
</div>

<div class="card">
    <h2 style="text-align: center; margin-bottom: 20px; color: #ffffff;">{{ ritual_data.ritual_need | capitalize }} Ritual</h2>
    
    <div style="font-size: 1.2rem; margin-bottom: 20px;">
        <strong>Duration:</strong> {{ ritual_data.duration }} minutes<br>
        <strong>Time of Day:</strong> {{ ritual_data.time_of_day | capitalize }}<br>
        <strong>Mood:</strong> {{ ritual_data.mood | capitalize }}<br>
        <strong>Environment:</strong> {{ ritual_data.environment | capitalize }}<br>
    </div>
    
    <div class="progress-bar" style="height: 10px; margin-bottom: 20px;">
        <div class="progress-fill" style="width: 0%;"></div>
    </div>
    
    <div id="ritual-steps">
        {% for step in ritual_steps %}
        <div class="ritual-step" style="margin-bottom: 15px;">
            <div style="font-weight: 500; color: #74b9ff;">{{ step.title }}</div>
            <div style="color: #ffffff;">{{ step.instruction }}</div>
        </div>
        {% endfor %}
    </div>
    
    <div style="text-align: center; margin-top: 30px;">
        <button id="complete-ritual" class="btn">✅ Complete Ritual</button>
    </div>
</div>

<script>
    // Simulate ritual progress
    let progress = 0;
    const totalDuration = {{ ritual_data.duration }};
    const progressBar = document.querySelector('.progress-fill');
    const ritualSteps = document.querySelectorAll('.ritual-step');
    
    function updateProgress() {
        progress += 1;
        const percentage = (progress / totalDuration) * 100;
        progressBar.style.width = percentage + '%';
        
        // Mark steps as completed
        ritualSteps.forEach((step, index) => {
            if (index < Math.floor((progress / totalDuration) * ritualSteps.length)) {
                step.style.opacity = 0.5;
            } else {
                step.style.opacity = 1;
            }
        });
        
        if (progress < totalDuration) {
            setTimeout(updateProgress, 60000); // Update every minute
        } else {
            // Ritual complete
            document.getElementById('complete-ritual').disabled = false;
            document.getElementById('complete-ritual').innerText = '🎉 Ritual Complete!';
        }
    }
    
    setTimeout(updateProgress, 1000); // Start after 1 second
</script>
'''

# Flask Routes
@app.route('/test')
def test_page():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <style>
            body { 
                background: #000; 
                color: #fff; 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px; 
            }
            h1 { color: #74b9ff; }
        </style>
    </head>
    <body>
        <h1>🔮 MYA3Reset: The Oracle - Test Page</h1>
        <p>If you can see this properly formatted, HTML rendering is working!</p>
        <a href="/" style="color: #74b9ff;">Go to Login Page</a>
    </body>
    </html>
    '''
    return html

@app.route('/template-test')
def template_test():
    try:
        return render_template('login.html')
    except Exception as e:
        return f"Template Error: {str(e)}"

@app.route('/')
def home():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    customer_id = session['customer_id']
    username = session['username']
    is_admin = session.get('is_admin', False)
    
    # Get user stats
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    # Get user's trial start date for days active
    cursor.execute('SELECT trial_start FROM users WHERE customer_id = ?', (customer_id,))
    result = cursor.fetchone()
    if result:
        trial_start = result[0]
        if isinstance(trial_start, str):
            trial_start_dt = datetime.fromisoformat(trial_start.replace('Z', '+00:00'))
        else:
            trial_start_dt = trial_start
        days_active = (datetime.now() - trial_start_dt).days + 1
    else:
        days_active = 1
    
    # Get sessions completed
    cursor.execute('SELECT COUNT(*) FROM user_sessions WHERE customer_id = ?', (customer_id,))
    sessions_completed = cursor.fetchone()[0]
    
    conn.close()
    
    overall_progress = 15  # Average of all modes
    
    return render_template('dashboard.html', 
                         customer_id=customer_id,
                         username=username,
                         is_admin=is_admin,
                         days_active=days_active, 
                         sessions_completed=sessions_completed,
                         overall_progress=overall_progress)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        step = request.form.get('step', 'single_step')
        
        if step == 'create_account':
            # Step 1: Create user account and Stripe customer, return setup intent
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            if password != confirm_password:
                return jsonify({'error': 'Passwords do not match'}), 400
            
            # Check if user already exists
            conn = sqlite3.connect('oracle.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE email = ? OR username = ?', (email, username))
            
            if cursor.fetchone():
                conn.close()
                return jsonify({'error': 'User already exists'}), 400
            
            # Create new user
            customer_id = generate_customer_id()
            password_hash = generate_password_hash(password)
            
            try:
                # Create Stripe customer (no payment method yet)
                stripe_customer = stripe.Customer.create(
                    email=email,
                    name=username,
                    metadata={'customer_id': customer_id}
                )
                
                # Create setup intent for saving payment method without charging
                setup_intent = stripe.SetupIntent.create(
                    customer=stripe_customer.id,
                    usage='off_session',  # For future payments
                    metadata={'customer_id': customer_id}
                )
                
                # Store user temporarily (without payment method)
                cursor.execute('''
                    INSERT INTO users (customer_id, username, email, password_hash, stripe_customer_id, subscription_status, trial_start, subscription_end)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (customer_id, username, email, password_hash, stripe_customer.id, 'trial_pending', datetime.now(), datetime.now() + timedelta(days=3)))
                
                conn.commit()
                conn.close()
                
                # Store customer_id in session for step 2
                session['temp_customer_id'] = customer_id
                
                return jsonify({
                    'success': True,
                    'client_secret': setup_intent.client_secret,
                    'customer_id': customer_id
                })
                
            except stripe.error.StripeError as e:
                conn.close()
                return jsonify({'error': f'Payment setup failed: {str(e)}'}), 400
        
        elif step == 'complete_registration':
            # Step 2: Complete registration with saved payment method
            payment_method_id = request.form.get('payment_method_id')
            setup_intent_id = request.form.get('setup_intent_id')
            customer_id = session.get('temp_customer_id')
            
            if not all([payment_method_id, setup_intent_id, customer_id]):
                return jsonify({'error': 'Missing required information'}), 400
            
            conn = sqlite3.connect('oracle.db')
            cursor = conn.cursor()
            
            try:
                # Get user info
                cursor.execute('SELECT username, stripe_customer_id FROM users WHERE customer_id = ?', (customer_id,))
                user_info = cursor.fetchone()
                if not user_info:
                    return jsonify({'error': 'User not found'}), 400
                
                username, stripe_customer_id = user_info
                
                # Store payment method ID for future billing
                cursor.execute('''
                    UPDATE users 
                    SET subscription_status = ?, payment_method_id = ?
                    WHERE customer_id = ?
                ''', ('trial', payment_method_id, customer_id))
                
                conn.commit()
                conn.close()
                
                # Log in user
                session['customer_id'] = customer_id
                session['username'] = username
                session['is_admin'] = False
                
                # Clear temp session data
                session.pop('temp_customer_id', None)
                
                return jsonify({'success': True})
                
            except Exception as e:
                conn.close()
                return jsonify({'error': f'Registration completion failed: {str(e)}'}), 400
        
        else:
            # Legacy single-step registration (fallback)
            return jsonify({'error': 'Legacy registration method not supported'}), 400
    
    return render_template('register.html', stripe_publishable_key=STRIPE_PUBLISHABLE_KEY)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('oracle.db')
        cursor = conn.cursor()
        cursor.execute('SELECT customer_id, username, password_hash, is_admin FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user[2], password):
            session['customer_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = bool(user[3])
            
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE customer_id = ?', 
                         (datetime.now(), user[0]))
            conn.commit()
            conn.close()
            
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
            conn.close()
    
    return render_template('login-working.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('login'))

@app.route('/subscribe')
def subscribe():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    subscribe_template = '''
    <div class="header">
        <h1>Upgrade to Premium 👑</h1>
        <p>🔮 Continue Your Transformation Journey</p>
    </div>
    
    <div class="card" style="text-align: center;">
        <h2 style="margin-bottom: 30px;">Your trial has ended</h2>
        <p>Subscribe to continue your transformation journey!</p>
        <p style="font-size: 2rem; color: #74b9ff; margin: 20px 0;">$19.99/month</p>
        <a href="{{ url_for('home') }}" class="btn">Continue with Trial</a>
    </div>
    '''
    
    content = render_template_string(subscribe_template)
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/profile')
def profile():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    # Get user profile data
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, email, subscription_status, trial_start, subscription_end, profile_data
        FROM users WHERE customer_id = ?
    ''', (session['customer_id'],))
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data:
        flash('User not found')
        return redirect(url_for('login'))
    
    # Parse profile data (contains preferences, profile picture, etc.)
    profile_data = json.loads(user_data[5] or '{}')
    
    # Calculate days active
    if user_data[3]:  # trial_start
        try:
            # Try parsing with microseconds first
            trial_date = datetime.strptime(user_data[3], '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            try:
                # Fallback to without microseconds
                trial_date = datetime.strptime(user_data[3], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # If all else fails, use current time
                trial_date = datetime.now()
        days_active = (datetime.now() - trial_date).days
    else:
        days_active = 0
    
    return render_template('profile.html',
                         username=user_data[0],
                         email=user_data[1],
                         subscription_status=user_data[2],
                         subscription_end=user_data[4],
                         days_active=days_active,
                         transformation_level=profile_data.get('transformation_level', 0),
                         user_profile_picture=profile_data.get('profile_picture'),
                         user_preferences=profile_data.get('preferences', {
                             'notifications': 'all',
                             'theme': 'dark'
                         }))

@app.route('/profile/update-account', methods=['POST'])
def update_account():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    
    if not username or not email:
        flash('Username and email are required')
        return redirect(url_for('profile'))
    
    try:
        conn = sqlite3.connect('oracle.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET username = ?, email = ?
            WHERE customer_id = ?
        ''', (username, email, session['customer_id']))
        conn.commit()
        conn.close()
        
        # Update session
        session['username'] = username
        
        flash('Account information updated successfully!')
    except sqlite3.IntegrityError:
        flash('Username or email already exists')
    except Exception as e:
        flash('Error updating account information')
    
    return redirect(url_for('profile'))

@app.route('/profile/change-password', methods=['POST'])
def change_password():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash('All password fields are required')
        return redirect(url_for('profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match')
        return redirect(url_for('profile'))
    
    if len(new_password) < 8:
        flash('Password must be at least 8 characters long')
        return redirect(url_for('profile'))
    
    # Verify current password
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE customer_id = ?', (session['customer_id'],))
    user = cursor.fetchone()
    
    if not user or not check_password_hash(user[0], current_password):
        flash('Current password is incorrect')
        conn.close()
        return redirect(url_for('profile'))
    
    # Update password
    new_password_hash = generate_password_hash(new_password)
    cursor.execute('''
        UPDATE users SET password_hash = ?
        WHERE customer_id = ?
    ''', (new_password_hash, session['customer_id']))
    conn.commit()
    conn.close()
    
    flash('Password updated successfully!')
    return redirect(url_for('profile'))

@app.route('/profile/update-picture', methods=['POST'])
def update_profile_picture():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    if 'profile_picture' not in request.files:
        flash('No file selected')
        return redirect(url_for('profile'))
    
    file = request.files['profile_picture']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('profile'))
    
    if file and allowed_file(file.filename):
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(app.root_path, 'uploads', 'profiles')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"{session['customer_id']}_{uuid.uuid4().hex[:8]}.{file.filename.rsplit('.', 1)[1].lower()}"
        filepath = os.path.join(upload_dir, filename)
        
        try:
            file.save(filepath)
            
            # Update user profile data
            conn = sqlite3.connect('oracle.db')
            cursor = conn.cursor()
            cursor.execute('SELECT profile_data FROM users WHERE customer_id = ?', (session['customer_id'],))
            current_data = cursor.fetchone()
            
            profile_data = json.loads(current_data[0] or '{}')
            profile_data['profile_picture'] = f'/uploads/profiles/{filename}'
            
            cursor.execute('''
                UPDATE users SET profile_data = ?
                WHERE customer_id = ?
            ''', (json.dumps(profile_data), session['customer_id']))
            conn.commit()
            conn.close()
            
            flash('Profile picture updated successfully!')
        except Exception as e:
            flash('Error uploading profile picture')
    else:
        flash('Invalid file type. Please upload an image file.')
    
    return redirect(url_for('profile'))

@app.route('/profile/update-preferences', methods=['POST'])
def update_preferences():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    notifications = request.form.get('notifications', 'all')
    theme = request.form.get('theme', 'dark')
    
    # Get current profile data
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    cursor.execute('SELECT profile_data FROM users WHERE customer_id = ?', (session['customer_id'],))
    current_data = cursor.fetchone()
    
    profile_data = json.loads(current_data[0] or '{}')
    profile_data['preferences'] = {
        'notifications': notifications,
        'theme': theme
    }
    
    cursor.execute('''
        UPDATE users SET profile_data = ?
        WHERE customer_id = ?
    ''', (json.dumps(profile_data), session['customer_id']))
    conn.commit()
    conn.close()
    
    flash('Preferences updated successfully!')
    return redirect(url_for('profile'))

@app.route('/profile/delete-account', methods=['GET', 'POST'])
def delete_account():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            conn = sqlite3.connect('oracle.db')
            cursor = conn.cursor()
            
            # Delete user data
            cursor.execute('DELETE FROM users WHERE customer_id = ?', (session['customer_id'],))
            conn.commit()
            conn.close()
            
            # Clear session
            session.clear()
            
            flash('Your account has been permanently deleted.')
            return redirect(url_for('home'))
        except Exception as e:
            flash('Error deleting account. Please contact support.')
            return redirect(url_for('profile'))
    
    return redirect(url_for('profile'))

@app.route('/profile/export-data')
def export_data():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = sqlite3.connect('oracle.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE customer_id = ?', (session['customer_id'],))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            # Create export data (excluding sensitive info like password hash)
            export_data = {
                'customer_id': user_data[1],
                'username': user_data[2],
                'email': user_data[3],
                'subscription_status': user_data[5],
                'trial_start': user_data[6],
                'subscription_end': user_data[7],
                'created_at': user_data[8],
                'last_login': user_data[9],
                'profile_data': user_data[10],
                'transformation_progress': user_data[12],
                'export_date': datetime.now().isoformat()
            }
            
            # You would typically generate a downloadable file here
            flash('Data export has been prepared. Check your email for download instructions.')
        else:
            flash('No data found for export')
    except Exception as e:
        flash('Error preparing data export')
    
    return redirect(url_for('profile'))

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check database for admin user
        conn = sqlite3.connect('oracle.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT password_hash, is_admin FROM users 
            WHERE email = ? AND is_admin = 1
        ''', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[0], password):
            session['admin_logged_in'] = True
            session['admin_email'] = email
            flash('Welcome back, CEO!')
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid admin credentials')
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Oracle Admin Login</title>
        <style>
            body { font-family: Arial; background: #1a1a2e; color: white; padding: 50px; text-align: center; }
            .login-form { max-width: 400px; margin: 0 auto; background: #16213e; padding: 40px; border-radius: 15px; }
            input { width: 100%; padding: 15px; margin: 10px 0; background: #2d3436; border: none; border-radius: 8px; color: white; }
            button { background: #e17055; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="login-form">
            <h1>🔮 Oracle Admin Access</h1>
            <p>CEO Login Required</p>
            <form method="POST">
                <input type="email" name="email" placeholder="CEO Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">🔐 Login as CEO</button>
            </form>
        </div>
    </body>
    </html>
    ''')

def admin_required(f):
    """Decorator to require admin authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_panel():
    # Get all users with detailed information
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    # Get users with subscription details
    cursor.execute('''
        SELECT customer_id, username, email, subscription_status, 
               created_at, last_login, subscription_end, stripe_customer_id,
               payment_method_id
        FROM users 
        ORDER BY created_at DESC
    ''')
    users_data = cursor.fetchall()
    
    # Format users data
    users = []
    for user in users_data:
        status_class = 'active' if user[3] == 'active' else 'trial' if user[3] == 'trial' else 'expired'
        users.append({
            'customer_id': user[0],
            'username': user[1],
            'email': user[2],
            'subscription_status': user[3],
            'status_class': status_class,
            'created_at': user[4],
            'last_login': user[5],
            'trial_end': user[6],
            'stripe_customer_id': user[7],
            'payment_method_id': user[8]
        })
    
    # Calculate statistics
    total_users = len(users)
    active_subscriptions = len([u for u in users if u['subscription_status'] == 'active'])
    trial_users = len([u for u in users if u['subscription_status'] == 'trial'])
    
    # Get failed payments (trial expired users)
    cursor.execute('''
        SELECT COUNT(*) FROM users 
        WHERE subscription_status = 'trial' AND subscription_end < datetime('now')
    ''')
    failed_payments = cursor.fetchone()[0]
    
    # Calculate monthly revenue (approximate)
    monthly_revenue = active_subscriptions * 19.99
    
    conn.close()
    
    stats = {
        'total_users': total_users,
        'active_subscriptions': active_subscriptions,
        'trial_users': trial_users,
        'failed_payments': failed_payments,
        'monthly_revenue': monthly_revenue
    }
    
    current_user = {'email': session.get('admin_email')}
    
    return render_template('admin-panel.html', 
                         users=users, 
                         stats=stats, 
                         current_user=current_user)

@app.route('/admin/user/<customer_id>')
@admin_required
def get_user_details(customer_id):
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT customer_id, username, email, subscription_status, 
               created_at, last_login, subscription_end, stripe_customer_id,
               payment_method_id
        FROM users WHERE customer_id = ?
    ''', (customer_id,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'customer_id': user[0],
            'username': user[1],
            'email': user[2],
            'subscription_status': user[3],
            'created_at': user[4],
            'last_login': user[5],
            'subscription_end': user[6],
            'stripe_customer_id': user[7],
            'payment_method_id': user[8]
        })
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/admin/force-logout/<customer_id>', methods=['POST'])
@admin_required
def force_logout_user(customer_id):
    """Force logout a specific user by clearing their session data"""
    try:
        # Update last_login to force re-authentication
        conn = sqlite3.connect('oracle.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET last_login = NULL WHERE customer_id = ?
        ''', (customer_id,))
        
        conn.commit()
        conn.close()
        
        # In a production app, you'd also clear their session from a session store
        # For now, we'll just mark them as logged out in the database
        
        return jsonify({'message': f'User {customer_id} has been logged out successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/suspend-user/<customer_id>', methods=['POST'])
@admin_required
def suspend_user(customer_id):
    """Suspend a user account"""
    try:
        conn = sqlite3.connect('oracle.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET subscription_status = 'suspended' WHERE customer_id = ?
        ''', (customer_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': f'User {customer_id} has been suspended'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/process-failed-payments', methods=['POST'])
@admin_required
def process_failed_payments():
    """Process all failed payments (expired trials)"""
    try:
        conn = sqlite3.connect('oracle.db')
        cursor = conn.cursor()
        
        # Get expired trial users with payment methods
        cursor.execute('''
            SELECT customer_id, email, stripe_customer_id, payment_method_id
            FROM users 
            WHERE subscription_status = 'trial' 
            AND subscription_end < datetime('now')
            AND payment_method_id IS NOT NULL
        ''')
        
        expired_users = cursor.fetchall()
        processed = 0
        successful = 0
        failed = 0
        
        for user in expired_users:
            processed += 1
            customer_id, email, stripe_customer_id, payment_method_id = user
            
            try:
                # Attempt to charge the user
                payment_intent = stripe.PaymentIntent.create(
                    amount=1999,  # $19.99
                    currency='usd',
                    customer=stripe_customer_id,
                    payment_method=payment_method_id,
                    confirm=True,
                    return_url='https://your-domain.com/return'
                )
                
                if payment_intent.status == 'succeeded':
                    # Update user to active subscription
                    cursor.execute('''
                        UPDATE users 
                        SET subscription_status = 'active',
                            subscription_end = datetime('now', '+1 month')
                        WHERE customer_id = ?
                    ''', (customer_id,))
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as payment_error:
                print(f"Payment failed for {email}: {payment_error}")
                failed += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'processed': processed,
            'successful': successful,
            'failed': failed
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/export-users')
@admin_required
def export_users():
    """Export users to CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT customer_id, username, email, subscription_status, 
               created_at, last_login, subscription_end
        FROM users 
        ORDER BY created_at DESC
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Customer ID', 'Username', 'Email', 'Status', 'Created', 'Last Login', 'Trial End'])
    
    # Write data
    for user in users:
        writer.writerow(user)
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=oracle_users.csv'
    
    return response

@app.route('/admin/mass-action/<action>', methods=['POST'])
@admin_required
def mass_action(action):
    """Perform mass actions on users"""
    try:
        conn = sqlite3.connect('oracle.db')
        cursor = conn.cursor()
        
        if action == 'expire_trials':
            cursor.execute('''
                UPDATE users 
                SET subscription_end = datetime('now', '-1 day')
                WHERE subscription_status = 'trial'
            ''')
            affected = cursor.rowcount
            message = f'Expired {affected} trial users'
            
        elif action == 'reset_login_times':
            cursor.execute('UPDATE users SET last_login = NULL')
            affected = cursor.rowcount
            message = f'Reset login times for {affected} users'
            
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': message})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_email', None)
    flash('Logged out successfully')
    return redirect(url_for('admin_login'))

@app.route('/admin/test', methods=['POST'])
@admin_required
def admin_test():
    """Simple test route to verify admin functionality"""
    return jsonify({'message': 'Admin test successful!', 'status': 'ok'})

@app.route('/ritual-creator')
def ritual_creator():
    """Custom Ritual Creator - Personalized ritual based on user preferences"""
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('ritual-creator.html')

@app.route('/ritual-session', methods=['POST'])
def ritual_session():
    """Start a personalized ritual session with countdown timer"""
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    # Get ritual parameters from form
    data = request.form
    
    # Extract ritual customization data
    ritual_data = {
        'birthday': data.get('birthday'),
        'mood': data.get('mood'),
        'environment': data.get('environment'),
        'duration': int(data.get('duration', 15)),  # Default 15 minutes
        'time_of_day': data.get('time_of_day'),
        'ritual_need': data.get('ritual_need'),
        'created_at': datetime.now().isoformat()
    }
    
    # Generate personalized ritual based on inputs
    ritual_steps = generate_ritual_steps(ritual_data)
    
    return render_template('ritual-session.html', 
                         ritual_data=ritual_data, 
                         ritual_steps=ritual_steps)

def generate_ritual_steps(ritual_data):
    """Generate personalized ritual steps based on user inputs"""
    birthday = ritual_data.get('birthday', '')
    mood = ritual_data.get('mood', '')
    environment = ritual_data.get('environment', '')
    duration = ritual_data.get('duration', 15)
    time_of_day = ritual_data.get('time_of_day', '')
    ritual_need = ritual_data.get('ritual_need', '')
    
    # Base ritual framework
    steps = []
    
    # Step 1: Opening/Grounding (always included)
    opening_step = {
        'title': '🌟 Opening & Grounding',
        'duration': max(2, duration // 7),  # ~15% of total time
        'instruction': f'Find your center in this {environment} space. Take 3 deep breaths and set your intention for {ritual_need.lower()}.'
    }
    
    if time_of_day == 'morning':
        opening_step['instruction'] += ' Welcome the new day with gratitude.'
    elif time_of_day == 'evening':
        opening_step['instruction'] += ' Release the day and prepare for rest.'
    elif time_of_day == 'afternoon':
        opening_step['instruction'] += ' Reset your energy for the remainder of your day.'
    
    steps.append(opening_step)
    
    # Step 2: Mood-based activity
    mood_activities = {
        'energized': {
            'title': '⚡ Energy Channeling',
            'instruction': 'Channel your high energy into powerful affirmations. Stand tall and declare your intentions.'
        },
        'calm': {
            'title': '🧘 Peaceful Meditation',
            'instruction': 'Embrace this calm state. Focus on your breath and visualize your goals manifesting.'
        },
        'stressed': {
            'title': '🌊 Stress Release',
            'instruction': 'Release tension through gentle movement or stretching. Let go of what no longer serves you.'
        },
        'tired': {
            'title': '🔋 Energy Restoration',
            'instruction': 'Focus on gentle movement and energizing breath work to restore your vitality.'
        },
        'anxious': {
            'title': '🌿 Anxiety Soothing',
            'instruction': 'Ground yourself with 4-7-8 breathing. Feel your connection to the earth beneath you.'
        },
        'excited': {
            'title': '✨ Excitement Focusing',
            'instruction': 'Direct your excitement toward your transformation goals. Visualize your success.'
        }
    }
    
    mood_step = mood_activities.get(mood, mood_activities['calm'])
    mood_step['duration'] = max(3, duration // 4)  # ~25% of total time
    steps.append(mood_step)
    
    # Step 3: Need-based core activity
    need_activities = {
        'energy': {
            'title': '🔥 Energy Activation',
            'instruction': 'Engage in dynamic movement, power poses, or energizing breathwork to boost your vitality.'
        },
        'grounding': {
            'title': '🌍 Earth Connection',
            'instruction': 'Visualize roots growing from your feet into the earth. Feel stable, centered, and secure.'
        },
        'peace': {
            'title': '☮️ Inner Peace Cultivation',
            'instruction': 'Practice mindful awareness, gentle meditation, or soothing self-talk for deep tranquility.'
        },
        'clarity': {
            'title': '🔍 Mental Clarity',
            'instruction': 'Focus on your breath, clear your mind, and set clear intentions for your path forward.'
        },
        'confidence': {
            'title': '💪 Confidence Building',
            'instruction': 'Stand in power poses, repeat confidence affirmations, and visualize yourself succeeding.'
        },
        'healing': {
            'title': '💚 Emotional Healing',
            'instruction': 'Practice self-compassion, forgiveness, and gentle healing visualization or movement.'
        }
    }
    
    core_step = need_activities.get(ritual_need, need_activities['energy'])
    core_step['duration'] = max(5, duration // 2)  # ~50% of total time
    steps.append(core_step)
    
    # Step 4: Integration & Closing
    remaining_time = duration - sum(step['duration'] for step in steps)
    closing_step = {
        'title': '🌟 Integration & Closing',
        'duration': max(1, remaining_time),
        'instruction': f'Take a moment to integrate this {ritual_need} energy into your being. Set an intention for how you\'ll carry this energy forward.'
    }
    
    if time_of_day == 'morning':
        closing_step['instruction'] += ' Step into your day with renewed purpose.'
    elif time_of_day == 'evening':
        closing_step['instruction'] += ' Carry this peace into your rest.'
    
    steps.append(closing_step)
    
    return steps

if __name__ == '__main__':
    init_db()
    print("🔮 Starting MYA3Reset: The Oracle...")
    print("📍 App will be available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
