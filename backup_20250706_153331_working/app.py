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
import csv
import datetime as dt
import re
from datetime import datetime, timedelta, date
from flask import Flask, request, render_template, render_template_string, redirect, url_for, session, flash, jsonify, send_from_directory, make_response, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from markupsafe import Markup

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Add custom nl2br filter for converting newlines to <br> tags
def nl2br(value):
    """Convert newlines to <br> tags"""
    if value is None:
        return ''
    return Markup(str(value).replace('\n', '<br>\n'))

app.jinja_env.filters['nl2br'] = nl2br

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_stripe_secret_key')

# Strategic Thinking: Scenario Drill (interactive exercise)
@app.route('/alpha-elite/strategic-mastery/strategic-thinking/scenario-exercise', methods=['GET', 'POST'])
def strategic_scenario_exercise():
    user_plan = None
    if request.method == 'POST':
        user_plan = request.form.get('plan', '').strip()
    return render_template('strategic-scenario-exercise.html', user_plan=user_plan)

# AI Framework: Model Design Challenge (interactive exercise)
@app.route('/alpha-elite/strategic-mastery/ai-framework/framework-exercise', methods=['GET', 'POST'])
def ai_framework_exercise():
    user_framework = None
    if request.method == 'POST':
        user_framework = request.form.get('framework', '').strip()
    return render_template('ai-framework-exercise.html', user_framework=user_framework)

# Schedule Performance: Prioritization Drill (interactive exercise)
@app.route('/alpha-elite/strategic-mastery/schedule-performance/prioritization-exercise', methods=['GET', 'POST'])
def schedule_performance_exercise():
    user_priorities = None
    if request.method == 'POST':
        user_priorities = request.form.get('priorities', '').strip()
    return render_template('schedule-performance-exercise.html', user_priorities=user_priorities)
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
    now = dt.datetime.now()
    
    # Check trial period (3 days)
    if status == 'trial':
        if isinstance(trial_start, str):
            trial_start_dt = dt.datetime.fromisoformat(trial_start.replace('Z', '+00:00'))
        else:
            trial_start_dt = trial_start
        if (now - trial_start_dt).days < 3:
            return True
    
    # Check active subscription
    if status == 'active' and subscription_end:
        if isinstance(subscription_end, str):
            sub_end_dt = dt.datetime.fromisoformat(subscription_end.replace('Z', '+00:00'))
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

# Progress tracking functions
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
    
    # Initialize transformation progress in user record
    cursor.execute('''
        UPDATE users SET transformation_progress = ?
        WHERE customer_id = ?
    ''', (json.dumps({
        'overall_progress': 0,
        'modes': {
            'alpha-elite': 0,
            'situationship': 0,
            'personality': 0,
            'rituals': 0
        },
        'total_sessions': 0,
        'achievements': [],
        'last_updated': dt.datetime.now().isoformat()
    }), customer_id))
    
    conn.commit()
    conn.close()

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
    
    # Get user transformation progress
    cursor.execute('''
        SELECT transformation_progress FROM users WHERE customer_id = ?
    ''', (customer_id,))
    user_progress = cursor.fetchone()
    
    # Get total sessions
    cursor.execute('''
        SELECT COUNT(*) FROM user_sessions WHERE customer_id = ?
    ''', (customer_id,))
    total_sessions = cursor.fetchone()[0]
    
    conn.close()
    
    # Parse transformation progress
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

def update_mode_progress(customer_id, mode_name, completion_percentage, achievements=None):
    """Update progress for a specific mode"""
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    # Ensure completion percentage is between 0 and 100
    completion_percentage = max(0, min(100, completion_percentage))
    
    # Update mode progress
    cursor.execute('''
        UPDATE mode_progress 
        SET completion_percentage = ?, 
            last_accessed = CURRENT_TIMESTAMP,
            achievements = ?
        WHERE customer_id = ? AND mode_name = ?
    ''', (completion_percentage, json.dumps(achievements or []), customer_id, mode_name))
    
    # If no row was updated, insert new record
    if cursor.rowcount == 0:
        cursor.execute('''
            INSERT INTO mode_progress (customer_id, mode_name, completion_percentage, achievements)
            VALUES (?, ?, ?, ?)
        ''', (customer_id, mode_name, completion_percentage, json.dumps(achievements or [])))
    
    # Update overall progress in user record
    progress_data = get_user_progress(customer_id)
    cursor.execute('''
        UPDATE users SET transformation_progress = ?
        WHERE customer_id = ?
    ''', (json.dumps({
        'overall_progress': progress_data['overall_progress'],
        'modes': {k: v['completion_percentage'] for k, v in progress_data['modes'].items()},
        'total_sessions': progress_data['total_sessions'],
        'last_updated': dt.datetime.now().isoformat()
    }), customer_id))
    
    conn.commit()
    conn.close()
    
    return progress_data['overall_progress']

def log_user_session(customer_id, mode, session_data=None, progress=0):
    """Log a user session for tracking"""
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO user_sessions (customer_id, mode, session_data, progress)
        VALUES (?, ?, ?, ?)
    ''', (customer_id, mode, json.dumps(session_data or {}), progress))
    
    conn.commit()
    conn.close()

def generate_customer_id():
    return f"ORC-{uuid.uuid4().hex[:8].upper()}"

# Routes
@app.route('/')
def home():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    customer_id = session['customer_id']
    
    # Get user progress
    progress_data = get_user_progress(customer_id)
    
    # Get user stats
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    
    # Calculate days active
    cursor.execute('SELECT trial_start FROM users WHERE customer_id = ?', (customer_id,))
    user_start = cursor.fetchone()
    if user_start and user_start[0]:
        try:
            start_date = dt.datetime.fromisoformat(user_start[0].replace('Z', '+00:00'))
        except:
            start_date = dt.datetime.now()
        days_active = (dt.datetime.now() - start_date).days + 1
    else:
        days_active = 1
    
    conn.close()
    
    # Prepare mode data for template
    mode_data = {
        'alpha-elite': progress_data['modes'].get('alpha-elite', {'completion_percentage': 0}),
        'situationship': progress_data['modes'].get('situationship', {'completion_percentage': 0}),
        'personality': progress_data['modes'].get('personality', {'completion_percentage': 0}),
        'rituals': progress_data['modes'].get('rituals', {'completion_percentage': 0})
    }
    
    return render_template('dashboard.html',
                         days_active=days_active,
                         sessions_completed=progress_data['total_sessions'],
                         overall_progress=progress_data['overall_progress'],
                         mode_data=mode_data)

@app.route('/dashboard')
def dashboard():
    """Alias for the home route"""
    return home()

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
                ''', (customer_id, username, email, password_hash, stripe_customer.id, 'trial_pending', dt.datetime.now(), dt.datetime.now() + timedelta(days=3)))
                
                # Initialize user progress at 0% for all modes
                initialize_user_progress(customer_id)
                
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
                         (dt.datetime.now(), user[0]))
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
    return redirect(url_for('login'))

# Mode routes
@app.route('/mode/<mode_name>')
def mode_page(mode_name):
    if 'customer_id' not in session:
        # Only set demo user for alpha-elite to maintain compatibility with existing code
        if mode_name == 'alpha-elite':
            session['customer_id'] = 'DEMO-USER'
            session['username'] = 'Demo User'
            session.modified = True
        else:
            return redirect(url_for('login'))
    
    customer_id = session['customer_id']
    
    # Valid modes
    valid_modes = ['alpha-elite', 'personality', 'rituals']
    if mode_name not in valid_modes:
        flash('Invalid mode')
        return redirect(url_for('home'))
    
    # Get user progress for this mode
    progress_data = get_user_progress(customer_id)
    mode_progress = progress_data['modes'].get(mode_name, {'completion_percentage': 0, 'level': 1})
    
    # Log session
    log_user_session(customer_id, mode_name, {'action': 'enter_mode'})
    
    # Route to appropriate template
    if mode_name == 'alpha-elite':
        return render_template('alpha-elite.html', progress=mode_progress)
    elif mode_name == 'personality':
        return render_template('assessment.html', progress=mode_progress)
    elif mode_name == 'rituals':
        return render_template('ritual-creator.html', progress=mode_progress)

@app.route('/situationship', endpoint='situationship_mode')
def situationship_mode():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    customer_id = session['customer_id']
    
    # Get user progress for situationship mode
    progress_data = get_user_progress(customer_id)
    mode_progress = progress_data['modes'].get('situationship', {'completion_percentage': 0, 'level': 1})
    
    # Log session
    log_user_session(customer_id, 'situationship', {'action': 'enter_mode'})
    
    return render_template('situationship.html', progress=mode_progress)

@app.route('/decision-game', methods=['GET', 'POST'])
@app.route('/decision-game/<relationship_type>', methods=['GET', 'POST'])
def decision_game(relationship_type='romantic'):
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    customer_id = session['customer_id']
    
    # Available relationship types
    available_types = ['romantic', 'friendship', 'professional']
    
    # Sample relationship scenarios for the decision game
    scenarios = [
        {
            'id': 1,
            'title': 'The Mixed Signals',
            'description': 'Someone you\'ve been dating for 3 weeks texts you daily but only wants to hang out late at night. They say they\'re "not ready for labels" but act possessive when you mention other friends.',
            'options': [
                {'id': 'a', 'text': 'Have a direct conversation about expectations', 'points': 10, 'feedback': 'Excellent! Clear communication is always the best approach.'},
                {'id': 'b', 'text': 'Go along with it and hope things change', 'points': 2, 'feedback': 'This often leads to more confusion. You deserve clarity.'},
                {'id': 'c', 'text': 'Start dating other people to make them jealous', 'points': 1, 'feedback': 'Games rarely lead to healthy relationships.'},
                {'id': 'd', 'text': 'Set clear boundaries about your availability', 'points': 8, 'feedback': 'Good! Setting boundaries shows self-respect.'}
            ]
        },
        {
            'id': 2,
            'title': 'The Breadcrumber',
            'description': 'Someone who used to date you regularly now only sends sporadic texts like "thinking of you" or likes your social media posts, but never makes concrete plans.',
            'options': [
                {'id': 'a', 'text': 'Tell them to stop contacting you unless they want to actually date', 'points': 10, 'feedback': 'Perfect! You\'re valuing your worth and time.'},
                {'id': 'b', 'text': 'Respond enthusiastically hoping they\'ll ask you out', 'points': 1, 'feedback': 'This encourages the breadcrumbing behavior.'},
                {'id': 'c', 'text': 'Ignore all their messages completely', 'points': 6, 'feedback': 'Not bad, but being direct is usually better.'},
                {'id': 'd', 'text': 'Ask them directly what they want from you', 'points': 9, 'feedback': 'Great approach! Direct communication cuts through confusion.'}
            ]
        },
        {
            'id': 3,
            'title': 'The Love Bomber',
            'description': 'Someone you just met is already talking about your future together, buying expensive gifts, and wanting to spend every day with you after just 2 weeks.',
            'options': [
                {'id': 'a', 'text': 'Enjoy the attention and go with the flow', 'points': 1, 'feedback': 'Red flag! Love bombing is often manipulation.'},
                {'id': 'b', 'text': 'Tell them to slow down and set a healthier pace', 'points': 10, 'feedback': 'Excellent! Healthy relationships develop gradually.'},
                {'id': 'c', 'text': 'Match their intensity to keep them interested', 'points': 2, 'feedback': 'This can lead to an unhealthy relationship dynamic.'},
                {'id': 'd', 'text': 'Politely distance yourself and observe their reaction', 'points': 8, 'feedback': 'Smart! Their reaction will tell you a lot about their character.'}
            ]
        }
    ]
    
    if request.method == 'POST':
        scenario_id = int(request.form.get('scenario_id'))
        choice = request.form.get('choice')
        
        # Find the selected scenario and choice
        selected_scenario = next(s for s in scenarios if s['id'] == scenario_id)
        selected_choice = next(opt for opt in selected_scenario['options'] if opt['id'] == choice)
        
        # Log the decision and update progress
        log_user_session(customer_id, 'situationship', {
            'action': 'decision_game', 
            'scenario_id': scenario_id,
            'choice': choice,
            'points': selected_choice['points']
        })
        
        progress_data = get_user_progress(customer_id)
        current_progress = progress_data['modes'].get('situationship', {}).get('completion_percentage', 0)
        new_progress = min(100, current_progress + 5)  # 5% progress per decision
        update_mode_progress(customer_id, 'situationship', new_progress)
        
        return render_template('decision-results.html',
                             scenario=selected_scenario,
                             choice=selected_choice,
                             scenarios=scenarios)
    
    # Get a random scenario for the game
    import random
    current_scenario = random.choice(scenarios)
    
    return render_template('decision-game.html', 
                          relationship_type=relationship_type,
                          available_types=available_types,
                          scenario=current_scenario,
                          scenarios=scenarios)

@app.route('/shadow-work', methods=['GET', 'POST'])
def shadow_work():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    customer_id = session['customer_id']
    
    # Hard-coded shadow work prompts since we may not have the table
    shadow_prompts = [
        "What patterns do you notice in your relationships that you'd like to change?",
        "When do you feel most insecure in relationships? What triggers this feeling?",
        "What do you fear most about being vulnerable with someone?",
        "How do you typically react when someone doesn't respond to your messages?",
        "What beliefs about love did you learn from your family growing up?",
        "When have you settled for less than you deserved in a relationship?",
        "What do you do when you feel jealous or threatened in a relationship?",
        "How do you handle conflict with romantic partners?",
        "What stories do you tell yourself when someone loses interest in you?",
        "In what ways do you self-sabotage in relationships?",
        "What is your relationship with jealousy and how does it show up?",
        "How do you handle rejection in romantic situations?",
        "What masks do you wear in relationships to feel accepted?",
        "When do you compromise your values to maintain a relationship?",
        "How do you react when your partner has close friendships with others?",
        "What childhood wounds still affect your adult relationships?",
        "How do you handle being alone versus being in relationship?",
        "What patterns of codependency do you recognize in yourself?",
        "How do you communicate your needs in relationships?",
        "What fears come up when someone gets too close to you?",
        "How do you handle power dynamics in your relationships?",
        "What stories do you tell yourself about your worth in relationships?",
        "How do you navigate physical and emotional intimacy?",
        "What role does perfectionism play in your relationships?",
        "How do you handle conflict and disagreement with loved ones?",
        "What boundaries do you struggle to maintain in relationships?",
        "How do you respond when someone doesn't meet your expectations?",
        "What aspects of yourself do you hide from romantic partners?",
        "How do you deal with the ending of relationships?",
        "What would change if you fully loved and accepted yourself?"
    ]
    
    # Get current prompt number from query parameter or default to 1
    prompt_number = int(request.args.get('prompt', 1))
    if prompt_number < 1 or prompt_number > len(shadow_prompts):
        prompt_number = 1
    
    current_prompt = shadow_prompts[prompt_number - 1]
    
    if request.method == 'POST':
        response = request.form.get('response', '').strip()
        emotional_intensity = request.form.get('emotional_intensity', 5)
        
        if response:
            # Store shadow work response in database
            conn = sqlite3.connect('oracle.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO shadow_work_responses (customer_id, prompt_id, response)
                VALUES (?, ?, ?)
            ''', (customer_id, prompt_number - 1, response))
            
            conn.commit()
            conn.close()
            
            # Log session and update progress
            log_user_session(customer_id, 'situationship', {'action': 'complete_shadow_work', 'prompt': prompt_number})
            progress_data = get_user_progress(customer_id)
            current_progress = progress_data['modes'].get('situationship', {}).get('completion_percentage', 0)
            new_progress = min(100, current_progress + 3)  # 3% progress per prompt
            update_mode_progress(customer_id, 'situationship', new_progress)
            
            flash('Shadow work response saved! 🌑 Deep insights recorded.')
            
            # Redirect to next prompt or back to first if completed
            next_prompt = prompt_number + 1 if prompt_number < len(shadow_prompts) else 1
            return redirect(url_for('shadow_work', prompt=next_prompt))
    
    # Get existing responses count for progress
    conn = sqlite3.connect('oracle.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM shadow_work_responses 
        WHERE customer_id = ?
    ''', (customer_id,))
    completed_prompts = cursor.fetchone()[0]
    conn.close()
    
    return render_template('shadow-work.html', 
                          prompt=current_prompt,
                          prompt_number=prompt_number,
                          total_prompts=len(shadow_prompts),
                          completed_prompts=completed_prompts)

@app.route('/boundary-setting', methods=['GET', 'POST'])
def boundary_setting():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('boundary-setting.html')

@app.route('/ai-coach', methods=['GET', 'POST'])
def ai_coach():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('ai-coach.html')

@app.route('/worth-assessment', methods=['GET', 'POST'])
def worth_assessment():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('assessment.html')

@app.route('/submit-shadow-work', methods=['POST'])
def submit_shadow_work():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    customer_id = session['customer_id']
    prompt_id = int(request.form.get('prompt_id', 0))
    response = request.form.get('response', '').strip()
    emotional_intensity = request.form.get('emotional_intensity', 5)
    
    if response:
        # Store shadow work response in database
        conn = sqlite3.connect('oracle.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO shadow_work_responses (customer_id, prompt_id, response)
            VALUES (?, ?, ?)
        ''', (customer_id, prompt_id, response))
        
        conn.commit()
        conn.close()
        
        # Log session and update progress
        log_user_session(customer_id, 'situationship', {'action': 'complete_shadow_work', 'prompt': prompt_id + 1})
        progress_data = get_user_progress(customer_id)
        current_progress = progress_data['modes'].get('situationship', {}).get('completion_percentage', 0)
        new_progress = min(100, current_progress + 3)  # 3% progress per prompt
        update_mode_progress(customer_id, 'situationship', new_progress)
        
        flash('Shadow work response saved! 🌑 Deep insights recorded.')
        
        # Redirect to next prompt
        next_prompt = prompt_id + 2  # Since prompt_id is 0-indexed
        return redirect(url_for('shadow_work', prompt=next_prompt))
    
    return redirect(url_for('shadow_work'))

# Run the application
if __name__ == '__main__':
    # Initialize the database
    init_db()
    print("🚀 Starting Oracle Platform on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
