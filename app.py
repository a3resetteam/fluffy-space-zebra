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
import openai
import logging

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# OpenAI configuration
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Set up logging
logging.basicConfig(level=logging.INFO)

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
    
    # Comprehensive relationship scenarios organized by type
    all_scenarios = {
        'romantic': [
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
        ],
        'friendship': [
            {
                'id': 4,
                'title': 'The One-Sided Friend',
                'description': 'Your friend always calls you when they need support but never seems available when you need them. They cancel plans last minute but expect you to drop everything for their emergencies.',
                'options': [
                    {'id': 'a', 'text': 'Have an honest conversation about the imbalance', 'points': 10, 'feedback': 'Excellent! Healthy friendships require reciprocity.'},
                    {'id': 'b', 'text': 'Continue being there for them hoping they\'ll change', 'points': 2, 'feedback': 'This enables the pattern and drains your energy.'},
                    {'id': 'c', 'text': 'Start being unavailable to teach them a lesson', 'points': 4, 'feedback': 'Passive-aggressive responses rarely solve problems.'},
                    {'id': 'd', 'text': 'Set boundaries about your availability', 'points': 9, 'feedback': 'Great! Protecting your time shows self-respect.'}
                ]
            },
            {
                'id': 5,
                'title': 'The Gossip Friend',
                'description': 'You discover that a close friend has been sharing your personal information with others. When confronted, they say "I was just concerned about you" and get defensive.',
                'options': [
                    {'id': 'a', 'text': 'End the friendship immediately', 'points': 6, 'feedback': 'Sometimes necessary, but consider if this is a pattern first.'},
                    {'id': 'b', 'text': 'Clearly communicate your boundaries about privacy', 'points': 10, 'feedback': 'Perfect! Clear boundaries are essential for trust.'},
                    {'id': 'c', 'text': 'Pretend it doesn\'t bother you to avoid conflict', 'points': 1, 'feedback': 'This will likely lead to more boundary violations.'},
                    {'id': 'd', 'text': 'Give them one more chance but limit what you share', 'points': 8, 'feedback': 'Good approach! Trust can be rebuilt with clear boundaries.'}
                ]
            },
            {
                'id': 6,
                'title': 'The Competitive Friend',
                'description': 'Your friend constantly tries to one-up your achievements, makes backhanded compliments, and seems to enjoy when things go wrong for you.',
                'options': [
                    {'id': 'a', 'text': 'Match their competitive energy', 'points': 2, 'feedback': 'This will escalate the unhealthy dynamic.'},
                    {'id': 'b', 'text': 'Address the behavior directly and calmly', 'points': 10, 'feedback': 'Excellent! Direct communication is key.'},
                    {'id': 'c', 'text': 'Gradually distance yourself from the friendship', 'points': 7, 'feedback': 'Sometimes necessary, but try communication first.'},
                    {'id': 'd', 'text': 'Stop sharing good news with them', 'points': 5, 'feedback': 'Protective but doesn\'t address the core issue.'}
                ]
            }
        ],
        'professional': [
            {
                'id': 7,
                'title': 'The Credit Stealer',
                'description': 'A colleague takes credit for your ideas in meetings and presents your work as their own. When you try to speak up, they interrupt or dismiss your contributions.',
                'options': [
                    {'id': 'a', 'text': 'Document everything and speak to your manager privately', 'points': 10, 'feedback': 'Excellent! Professional and strategic approach.'},
                    {'id': 'b', 'text': 'Confront them aggressively in the next meeting', 'points': 3, 'feedback': 'This could backfire and make you look unprofessional.'},
                    {'id': 'c', 'text': 'Stop sharing ideas to protect yourself', 'points': 5, 'feedback': 'Protective but limits your career growth.'},
                    {'id': 'd', 'text': 'Send follow-up emails copying your manager after meetings', 'points': 9, 'feedback': 'Smart! Creates a paper trail professionally.'}
                ]
            },
            {
                'id': 8,
                'title': 'The Boundary Pusher',
                'description': 'Your boss frequently contacts you after hours and on weekends for non-urgent matters. They expect immediate responses and make comments about "commitment" when you don\'t reply instantly.',
                'options': [
                    {'id': 'a', 'text': 'Set clear communication boundaries about after-hours contact', 'points': 10, 'feedback': 'Perfect! Professional boundaries are essential for work-life balance.'},
                    {'id': 'b', 'text': 'Always respond immediately to show dedication', 'points': 2, 'feedback': 'This reinforces unhealthy expectations and leads to burnout.'},
                    {'id': 'c', 'text': 'Ignore after-hours messages completely', 'points': 4, 'feedback': 'Could create conflict without addressing the issue.'},
                    {'id': 'd', 'text': 'Discuss workload and priorities during business hours', 'points': 8, 'feedback': 'Good approach! Addresses the root issue professionally.'}
                ]
            },
            {
                'id': 9,
                'title': 'The Toxic Teammate',
                'description': 'A team member consistently undermines group projects, speaks negatively about colleagues, and creates a hostile work environment. Others are afraid to speak up.',
                'options': [
                    {'id': 'a', 'text': 'Document incidents and report to HR', 'points': 10, 'feedback': 'Excellent! Protecting the team\'s wellbeing is important.'},
                    {'id': 'b', 'text': 'Ignore the behavior and focus on your own work', 'points': 3, 'feedback': 'This allows toxic behavior to continue affecting others.'},
                    {'id': 'c', 'text': 'Confront them directly about their behavior', 'points': 7, 'feedback': 'Could be effective but might escalate the situation.'},
                    {'id': 'd', 'text': 'Build alliances with other teammates first', 'points': 8, 'feedback': 'Good strategy! Collective action is often more effective.'}
                ]
            }
        ]
    }
    
    # Get scenarios for the specific relationship type
    scenarios = all_scenarios.get(relationship_type, all_scenarios['romantic'])
    
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
                             relationship_type=relationship_type,
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

@app.route('/boundary-program/day/<int:day>')
def boundary_program_day(day):
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    # Daily program content
    program_content = {
        1: {
            'title': 'Foundation Day: Understanding Your Boundaries',
            'objective': 'Complete your personal boundary assessment and identify key areas for growth',
            'exercises': [
                {
                    'name': 'Personal Boundary Audit',
                    'description': 'Review the past week and identify 3 situations where you felt your boundaries were crossed',
                    'type': 'reflection',
                    'time': '15 minutes'
                },
                {
                    'name': 'Boundary Values Clarification', 
                    'description': 'List your top 5 personal values and how boundaries protect them',
                    'type': 'writing',
                    'time': '20 minutes'
                },
                {
                    'name': 'Practice Phrase: "Let me think about it"',
                    'description': 'Use this phrase 3 times today instead of immediately saying yes or no',
                    'type': 'practice',
                    'time': 'Throughout day'
                }
            ],
            'daily_affirmation': 'I have the right to protect my time, energy, and well-being through healthy boundaries.',
            'progress_tip': 'Start small - even recognizing when a boundary is needed is progress!'
        },
        2: {
            'title': 'Identification Day: Recognizing Boundary Violations',
            'objective': 'Learn to quickly identify when your boundaries are being tested or crossed',
            'exercises': [
                {
                    'name': 'Body Signal Awareness',
                    'description': 'Notice physical sensations when someone asks something of you - tension, discomfort, or resistance',
                    'type': 'mindfulness',
                    'time': '10 minutes'
                },
                {
                    'name': 'Trigger Mapping',
                    'description': 'Identify the top 3 people and situations that make boundary-setting difficult for you',
                    'type': 'analysis',
                    'time': '15 minutes'
                },
                {
                    'name': 'Practice Phrase: "I need to check my schedule"',
                    'description': 'Buy yourself time before committing to requests',
                    'type': 'practice',
                    'time': 'Throughout day'
                }
            ],
            'daily_affirmation': 'I trust my instincts when something doesn\'t feel right for me.',
            'progress_tip': 'Your discomfort is valuable information - listen to it!'
        }
        # Additional days would continue here...
    }
    
    if day not in program_content:
        return redirect(url_for('boundary_setting'))
    
    day_content = program_content[day]
    customer_id = session['customer_id']
    
    # Log program engagement
    log_user_session(customer_id, 'boundary_program', {
        'action': 'day_access',
        'day': day,
        'timestamp': dt.datetime.now().isoformat()
    })
    
    return render_template('boundary-program-day.html', 
                          day=day, 
                          content=day_content,
                          total_days=21)

@app.route('/ai-coach', methods=['GET', 'POST'])
def ai_coach():
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('ai-coach.html')

@app.route('/ai-coach/chat', methods=['POST'])
def ai_coach_chat():
    """Handle AI coach conversations with real AI responses"""
    if 'customer_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        coach_type = data.get('coach_type', 'supportive')
        conversation_history = data.get('conversation_history', [])
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Generate AI response
        ai_response = generate_ai_coach_response(user_message, coach_type, conversation_history)
        
        # Store conversation in database
        store_ai_conversation(session['customer_id'], coach_type, user_message, ai_response)
        
        return jsonify({
            'response': ai_response,
            'coach_type': coach_type,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"AI Coach error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def generate_ai_coach_response(user_message, coach_type, conversation_history):
    """Generate AI response based on coach type and conversation context"""
    
    # Add detailed logging
    logging.info(f"Generating AI response for coach type: {coach_type}")
    logging.info(f"OpenAI API Key exists: {bool(openai.api_key)}")
    
    # Check if API key is available - use intelligent fallback if not
    if not openai.api_key or openai.api_key == "your_openai_api_key_here":
        logging.warning("No valid OpenAI API key found - using advanced fallback system")
        return generate_advanced_fallback_response(user_message, coach_type, conversation_history)
    
    # Coach personalities and system prompts
    coach_prompts = {
        'supportive': {
            'name': 'Maya',
            'personality': 'You are Maya, a supportive and empathetic relationship coach. You provide gentle, nurturing guidance with emotional validation. You speak with warmth, compassion, and understanding. You focus on emotional healing, self-love, and gentle boundary setting.',
            'tone': 'warm, empathetic, validating',
            'approach': 'emotional support and gentle guidance'
        },
        'direct': {
            'name': 'Dana', 
            'personality': 'You are Dana, a direct and no-nonsense relationship coach. You provide tough love and reality checks. You cut through excuses and call out self-defeating patterns. You speak with confidence and directness while still being supportive.',
            'tone': 'direct, honest, challenging but caring',
            'approach': 'tough love and accountability'
        },
        'strategic': {
            'name': 'Sam',
            'personality': 'You are Sam, a strategic and analytical relationship coach. You provide logical frameworks and data-driven insights. You focus on patterns, systems, and step-by-step action plans. You speak with clarity and precision.',
            'tone': 'analytical, logical, systematic',
            'approach': 'strategic planning and systematic analysis'
        },
        'intuitive': {
            'name': 'Iris',
            'personality': 'You are Iris, an intuitive and spiritually-minded relationship coach. You focus on inner wisdom, spiritual growth, and soul-level connections. You speak with depth, wisdom, and spiritual insight.',
            'tone': 'wise, spiritual, intuitive',
            'approach': 'spiritual wisdom and inner knowing'
        }
    }
    
    coach_info = coach_prompts.get(coach_type, coach_prompts['supportive'])
    
    # Build conversation context
    context_messages = []
    
    # Add system prompt
    system_prompt = f"""
{coach_info['personality']}

You are an expert relationship and situationship coach specializing in helping people navigate complex romantic relationships, unclear relationship statuses, communication issues, and personal growth.

Your coaching approach is {coach_info['approach']}. Your tone should be {coach_info['tone']}.

Guidelines:
- Keep responses to 2-3 paragraphs maximum
- Be specific and actionable
- Address the user's emotional state
- Provide practical next steps when appropriate
- Use the coach's characteristic style and personality
- Focus on relationship dynamics, communication, boundaries, and self-worth
- Ask insightful follow-up questions when relevant
- Remember this is about relationships, dating, and personal growth

Current situation context: The user is seeking relationship guidance and coaching.
"""
    
    context_messages.append({"role": "system", "content": system_prompt})
    
    # Add conversation history (last 6 messages for context)
    if conversation_history:
        recent_history = conversation_history[-6:]
        for msg in recent_history:
            if msg.get('type') == 'user':
                context_messages.append({"role": "user", "content": msg.get('message', '')})
            elif msg.get('type') == 'coach':
                context_messages.append({"role": "assistant", "content": msg.get('message', '')})
    
    # Add current user message
    context_messages.append({"role": "user", "content": user_message})
    
    try:
        # Create client instance
        client = openai.OpenAI(api_key=openai.api_key)
        logging.info(f"Created OpenAI client. Has API key: {bool(client.api_key)}")
        
        try:
            # Generate response using OpenAI
            logging.info("Sending request to OpenAI API...")
            response = client.chat.completions.create(
                model="gpt-4", 
                messages=context_messages,
                max_tokens=500,
                temperature=0.8,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            logging.info("Received successful response from OpenAI API")
        except Exception as e:
            logging.error(f"OpenAI API request failed: {str(e)}")
            raise e
        
        ai_response = response.choices[0].message.content.strip()
        
        # Add coach-specific formatting/emoji based on type
        if coach_type == 'supportive':
            if not any(emoji in ai_response for emoji in ['💚', '🤗', '💕', '✨', '🌸']):
                ai_response += ' 💚'
        elif coach_type == 'direct':
            if not any(emoji in ai_response for emoji in ['🔥', '💪', '💥', '🎯']):
                ai_response += ' 🔥'
        elif coach_type == 'strategic':
            if not any(emoji in ai_response for emoji in ['🧠', '📊', '📈', '🎯']):
                ai_response += ' 🧠'
        elif coach_type == 'intuitive':
            if not any(emoji in ai_response for emoji in ['🔮', '✨', '🌙', '🦋', '🌟']):
                ai_response += ' ✨'
        
        return ai_response
        
    except Exception as e:
        logging.error(f"OpenAI API error: {str(e)}")
        # Fallback to enhanced rule-based responses if AI fails
        return generate_fallback_response(user_message, coach_type)

def generate_advanced_fallback_response(user_message, coach_type, conversation_history):
    """Generate intelligent fallback responses based on message content and coach type"""
    
    # Check for very simple help requests first
    user_message_lower = user_message.lower()
    help_phrases = ["need help", "need advice", "need support", "help me", "advice please", "feeling", "i feel"]
    is_simple_help_request = len(user_message.split()) < 20 and any(phrase in user_message_lower for phrase in help_phrases)
    
    # First, try to extract specific elements from the user's message
    user_name = extract_name(user_message, conversation_history)
    situation_duration = extract_duration(user_message)
    emotion = extract_emotion(user_message)
    relationship_status = extract_relationship_status(user_message)
    concern = extract_main_concern(user_message)
    
    # FOR TESTING ONLY - Write to a debug file
    if "my boyfriend just disappeared on my birthday" in user_message.lower():
        with open("debug_response.txt", "a") as f:
            f.write(f"\nTESTING BIRTHDAY GHOSTING RESPONSE\n")
            f.write(f"Message: {user_message}\n")
            f.write(f"Coach Type: {coach_type}\n")
            f.write(f"Detected Emotion: {emotion}\n")
            f.write(f"Detected Concern: {concern}\n")
            f.write(f"Detected Status: {relationship_status}\n")
    
    logging.info(f"Extracted from message - Emotion: {emotion}, Concern: {concern}, Status: {relationship_status}")
    
    # Special case - always prioritize abandonment_event concern over emotion
    if concern == 'abandonment_event' or concern == 'abandonment':
        # For abandonment cases, always use our specialized abandonment responses
        # Skip the emotional response generation entirely
        with open('test_abandonment_debug.txt', 'a') as f:
            f.write(f"Detected abandonment in: {user_message}\n")
            f.write(f"Concern: {concern}, Emotion: {emotion}\n")
            
    # For simple messages like "I feel sad", prioritize emotional support
    elif (len(user_message.split()) < 15 and emotion) or is_simple_help_request:
        # For very short emotional messages, use our direct emotional response system
        return generate_emotional_response(user_message, emotion, coach_type)
    
    # Analyze user message for keywords to create more targeted responses
    keywords = {
        'relationship': ['relationship', 'partner', 'boyfriend', 'girlfriend', 'spouse', 'husband', 'wife', 'marriage', 'dating'],
        'communication': ['talk', 'communication', 'said', 'told', 'conversation', 'discuss', 'texting', 'message', 'call'],
        'feelings': ['feel', 'feeling', 'hurt', 'sad', 'angry', 'happy', 'confused', 'anxious', 'love', 'hate'],
        'conflict': ['fight', 'argument', 'conflict', 'disagree', 'issue', 'problem', 'upset', 'mad', 'furious'],
        'future': ['future', 'commit', 'next step', 'moving forward', 'planning', 'marry', 'serious', 'long-term'],
        'boundaries': ['boundary', 'boundaries', 'respect', 'space', 'need', 'distance', 'time', 'break'],
        'ex': ['ex', 'broke up', 'previous relationship', 'back together', 'history', 'past', 'former'],
        'dating': ['dating', 'date', 'seeing each other', 'talking stage', 'situationship', 'casual', 'exclusive'],
        'trust': ['trust', 'suspicious', 'cheating', 'faithful', 'loyal', 'honesty', 'lies', 'betrayal'],
        'intimacy': ['intimate', 'sex', 'physical', 'affection', 'touch', 'close', 'connection'],
        'family': ['family', 'parents', 'mother', 'father', 'siblings', 'children', 'kids'],
        'self_worth': ['worth', 'value', 'deserve', 'good enough', 'self-esteem', 'confidence']
    }
    
    # Detect topics in the user message
    detected_topics = []
    topic_scores = {}
    user_message_lower = user_message.lower()
    
    # Calculate score for each topic based on keyword matches
    for topic, topic_keywords in keywords.items():
        score = sum(3 if keyword in user_message_lower else 0 for keyword in topic_keywords)
        
        # Additional scoring based on context
        if topic == 'feelings' and emotion:
            score += 5
        if topic == 'trust' and concern == 'trust':
            score += 5
        if topic == 'boundaries' and concern in ['boundaries', 'space']:
            score += 5
        if topic == 'conflict' and emotion in ['angry', 'hurt']:
            score += 3
        
        # Score from conversation history
        if conversation_history:
            recent_messages = [msg.get('message', '') for msg in conversation_history[-3:] if msg.get('type') == 'user']
            for msg in recent_messages:
                msg_lower = msg.lower()
                score += sum(1 if keyword in msg_lower else 0 for keyword in topic_keywords)
        
        if score > 0:
            topic_scores[topic] = score
    
    # Add high-scoring topics, prioritizing most relevant
    sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    detected_topics = [topic for topic, score in sorted_topics if score >= 3]
    
    # Add main concern if detected
    if concern and concern in keywords:
        detected_topics.insert(0, concern)
    
    # If no topics detected, use general responses
    if not detected_topics:
        detected_topics = ['general']
    
    # Remove duplicates while preserving order
    detected_topics = list(dict.fromkeys(detected_topics))
    
    # Generate responses based on coach type and detected topics
    coach_responses = {
        'supportive': {
            'general': [
                "Thank you for sharing this with me{user_name}. I'm here to support you through whatever you're going through {duration}. 💚 Your {emotion} feelings are completely valid and important.",
                "I appreciate you opening up about your {concern}. This sounds challenging{user_name}, and I want you to know I'm here for you. 🤗 In your {status}, what support do you need most right now?",
                "I'm listening and I care deeply about what you're experiencing in this {status}. You deserve to be heard and supported through this {concern}. 💚 What would feel most nurturing for you today?"
            ],
            'relationship': [
                "Relationships can bring up so many emotions{user_name}, and what you're experiencing {duration} is completely valid. 💚 How is this {status} affecting your wellbeing day to day?",
                "The way you're feeling in this {status} matters deeply. You deserve care, respect, and clear communication {duration}. 💕 What does your heart truly need right now?",
                "It takes courage to navigate these {status} challenges{user_name}. I'm here to support you through this process with your {concern}. ✨ What would a loving relationship feel like to you?"
            ],
            'communication': [
                "Communication can be so challenging{user_name}, especially when emotions are involved in a {status}. 💚 What would you like to express about your {concern} that hasn't been said yet?",
                "When communication breaks down {duration}, it can feel really isolating. Your need for clear, honest conversation about this {concern} is valid. 🤗 How might you create space for that?",
                "I hear that communication is a struggle in your {status} right now. You deserve to be heard and understood about your {concern}. 💕 What conversation would bring you the most peace?"
            ],
            'feelings': [
                "Your {emotion} feelings are wise messengers telling you something important{user_name}. 💚 What do you think these emotions are trying to tell you about your needs in this {status}?",
                "It's okay to feel {emotion}. Your emotions {duration} are valid signals about what matters to you. 🤗 How can you honor these feelings about your {concern} today?",
                "I hear the depth of your feelings in your words about this {concern}. Thank you for being vulnerable. 💕 What would it look like to tend to these emotions with compassion?"
            ]
        },
        'direct': {
            'general': [
                "Let's cut to the chase{user_name} - what's really going on with your {concern}? 🔥 No sugarcoating, what's the real issue you're avoiding {duration}?",
                "Time for some honest talk about your {status}. You already know what needs to happen with this {concern}, don't you? 🎯 What action are you avoiding taking?",
                "I'm going to be straight with you{user_name} because that's what you need right now with this {concern}. 💪 What tough decision about your {status} have you been putting off?"
            ],
            'relationship': [
                "This {status} is showing you exactly what it is {duration} - are you paying attention to the patterns? 🔥 What reality about your {concern} are you refusing to accept?",
                "Let's be real{user_name} - if they wanted to give you what you need in this {status}, they would. Full stop. 💥 What standards are you compromising on {duration}?",
                "You're feeling {emotion} because you're accepting behavior in this {status} that doesn't meet your standards. 🎯 How much longer are you willing to settle for this {concern}?"
            ],
            'boundaries': [
                "Your boundaries in this {status} are only as strong as your willingness to enforce them{user_name}. 🔥 What boundary related to your {concern} do you need to reinforce today?",
                "Stop hoping they'll respect limits you haven't clearly set {duration}. 💪 What boundary in this {status} needs to be non-negotiable starting now?",
                "Boundaries aren't requests - they're requirements. Period. 🎯 Which boundary about your {concern} are you letting slide that needs to be firm?"
            ],
            'trust': [
                "Trust is earned through actions, not words{user_name}. 🔥 What patterns in this {status} are showing you the truth about trust?",
                "You're feeling {emotion} because your intuition is screaming at you about this {concern}. 💪 When will you start trusting yourself over their excuses?",
                "Let's be crystal clear: broken trust {duration} is a serious red flag. 🎯 What's your concrete plan if this happens again?"
            ]
        },
        'strategic': {
            'general': [
                "Let's analyze your {concern} objectively{user_name}. 🧠 What are the key variables at play in your {status}, and what patterns do you notice {duration}?",
                "Looking at your {status} systematically, I see several factors to consider. 📊 What data points about your {concern} would help clarify your next steps?",
                "This {concern} requires strategic thinking{user_name}. 🎯 If we break down your {status} into components, what's the highest priority issue to address first?"
            ],
            'future': [
                "Let's develop a clear decision framework for your next steps with this {concern}. 🧠 What are your non-negotiable requirements for moving forward in this {status} {duration}?",
                "If we project six months into the future of your {status}, what outcome would indicate success to you{user_name}? 📊 What metrics for your {concern} would show progress?",
                "Strategic planning for your {concern} requires clear objectives. 🎯 What specifically needs to change in your {status}, and by when, for this to be viable {duration}?"
            ],
            'conflict': [
                "Conflict often follows predictable patterns{user_name}. 🧠 What's the recurring cycle you're observing in these {concern} disagreements {duration}?",
                "Let's map out the {concern} dynamics objectively in your {status}. 📊 What triggers escalation, and where are the potential intervention points?",
                "A strategic approach to resolving your {concern} starts with root cause analysis. 🎯 What underlying need in your {status} isn't being addressed {duration}?"
            ],
            'communication': [
                "Let's analyze the communication patterns in your {status}{user_name}. 🧠 What's the frequency, depth, and reciprocity ratio you're experiencing?",
                "Communication effectiveness can be measured through specific metrics. 📊 In your {status}, what concrete examples demonstrate the {concern} issues {duration}?",
                "Strategic communication improvements require baseline data and clear goals. 🎯 What would successful communication in your {status} look like specifically?"
            ]
        },
        'intuitive': {
            'general': [
                "Your inner wisdom already knows the answer about your {concern} you seek{user_name}. ✨ When you quiet your mind and listen to your heart, what does it say about your {status}?",
                "This {concern} is offering you an opportunity for profound soul growth. 🔮 What is your spirit trying to learn through this {status} experience {duration}?",
                "Trust the energy you feel about your {concern} - it's rarely wrong{user_name}. 🌙 What would your highest self do in this {status} situation?"
            ],
            'feelings': [
                "These {emotion} emotions are sacred messengers from your deeper self about your {status}. ✨ What truth about your {concern} are they revealing that your mind might be resisting?",
                "When you feel into your {concern} with your whole being{user_name}, not just your mind, what becomes clear about your {status}? 🔮 What does your intuition say?",
                "Your emotional landscape {duration} is showing you your soul's path. 🌟 Which feelings about your {concern} feel expansive, and which feel constrictive in this {status}?"
            ],
            'future': [
                "Close your eyes and envision yourself one year from now{user_name}, having chosen your highest path with this {concern}. ✨ What does that version of you want you to know about your {status}?",
                "The universe is always guiding you toward your authentic destiny through your {status}. 🔮 What synchronicities about your {concern} have been appearing {duration} to show you the way?",
                "Your future self beyond this {concern} is already whole, already healed{user_name}. 🌙 What would that version of you advise about your {status} in this moment?"
            ],
            'trust': [
                "Your soul always knows the truth about your {status}{user_name}. ✨ What whispers of intuition about your {concern} have you been ignoring?",
                "Trust is a sacred energy exchange that reveals your deepest patterns. 🔮 What soul lesson about trust is being presented through this {concern} {duration}?",
                "When you connect with your higher wisdom, what guidance do you receive about the truth in your {status}? 🌟 Which path feels most aligned with your authentic self?"
            ]
        }
    }
    
    # Choose topic - prefer specific topics but fallback to general
    available_topics = [topic for topic in detected_topics if topic in coach_responses.get(coach_type, {}) and topic != 'general']
    
    # Special case: if emotion is detected but no other strong topics, prioritize 'feelings' topic
    if emotion and (not available_topics or (len(user_message.split()) < 20 and 'feelings' in coach_responses.get(coach_type, {}))):
        chosen_topic = 'feelings'
    elif 'boundaries' in available_topics and not any(word in user_message.lower() for word in ['boundary', 'boundaries', 'limit', 'space']):
        # Don't use boundaries topic unless explicitly mentioned
        available_topics.remove('boundaries')
        chosen_topic = random.choice(available_topics) if available_topics else 'general'
    else:
        chosen_topic = random.choice(available_topics) if available_topics else 'general'
    
    # Get responses for this coach type and topic
    coach_type_responses = coach_responses.get(coach_type, coach_responses['supportive'])
    topic_responses = coach_type_responses.get(chosen_topic, coach_type_responses.get('general', []))
    
    if not topic_responses:
        # Ultimate fallback - use basic responses
        return generate_fallback_response(user_message, coach_type)
    
    # Select response template
    response_template = random.choice(topic_responses)
    
    # Special handling for abandonment and abandonment_event scenarios
    if concern == 'abandonment' or concern == 'abandonment_event':
        abandonment_responses = {
            'supportive': {
                'abandonment': [
                    "I'm so sorry you're experiencing this ghosting situation{user_name}. Being suddenly cut off is incredibly painful and confusing. 💚 Your feelings of {emotion} are completely valid. This behavior says everything about THEIR character and nothing about your worth. First, give yourself permission to feel hurt - it's a normal response. Then, focus on self-care - connect with people who value you consistently, journal your feelings, and remember that someone who disappears without explanation isn't someone who can meet your relationship needs long-term.",
                    "Being ghosted can feel so devastating and disorienting{user_name}. You deserve clear communication and closure, not silence. 🤗 Listen carefully: their disappearing act isn't about your value - it's about their inability to communicate like an adult. Don't waste time trying to figure out 'why' - that path leads to unnecessary self-blame. Instead, lean on your support system, establish a temporary no-contact period, and focus on activities that remind you of your worth outside of this relationship.",
                    "I hear how painful this sudden disappearance has been for you{user_name}. Being ghosted can trigger deep feelings of worthlessness, but this reflects their character, not your value. 💕 Here's what you need to know: when someone ghosts you, they're showing you they lack the emotional maturity for a healthy relationship. Set a time limit on your waiting (I suggest 3-5 days max), then move forward assuming they won't return. Don't leave your life on hold for someone who couldn't even give you the respect of a proper conversation."
                ],
                'abandonment_event': [
                    "Being ghosted on your birthday is particularly painful and I'm truly sorry you're experiencing this{user_name}. This special day deserved to be honored, and you deserve to be celebrated. 💚 Let me be clear: someone who disappears on your birthday is showing you exactly where you stand in their priorities, and that's not where you deserve to be. This isn't small - it's a significant breach of basic relationship courtesy. Focus first on reclaiming your birthday - reach out to people who genuinely care, treat yourself to something special, and remember that someone who truly values you would never leave you hanging on an important day.",
                    "I'm really sorry they disappeared on such an important occasion{user_name}. Having a special event like your birthday impacted by someone's absence adds an extra layer of pain. 🤗 Here's the truth: ghosting you on your birthday is showing a profound lack of respect and consideration. This isn't something small to overlook - it's revealing how they handle their responsibilities toward people they claim to care about. Your hurt is completely justified. Give yourself permission to celebrate anyway - with friends, family, or even solo. You deserve celebration regardless of someone else's poor behavior.",
                    "Being abandoned on your special day is heartbreaking, and your feelings of {emotion} are completely valid{user_name}. This special event should have been about celebrating you, not managing this painful absence. 💕 The person who disappears on your birthday is showing you clearly that they can't be counted on for the basics of relationship consideration. Take this as important information about their character. Don't chase them for explanations - focus instead on surrounding yourself with people who show up for you consistently. Make a plan to properly celebrate yourself within the next week - don't let their absence steal your joy completely."
                ]
            },
            'direct': {
                'abandonment': [
                    "Let's be clear{user_name} - ghosting is cowardice, plain and simple. 🔥 Someone who disappears without explanation isn't worthy of your energy. Here's what you need to do: First, stop making excuses for them - there is NO valid reason to ghost someone you care about. Second, establish a firm no-contact rule - don't chase, text, or check their social media. Third, evaluate what red flags you might have overlooked earlier. And finally, refuse to accept this treatment in the future - anyone who can't communicate directly doesn't deserve access to your life.",
                    "Ghosting shows you exactly who they are{user_name} - someone who lacks the courage for difficult conversations. 💪 Stop romanticizing their behavior - this isn't mysterious or complicated, it's emotional immaturity. Cut your losses now instead of wasting more time. Block their number for at least 30 days to break the checking habit. If they come back with excuses, remember that emergencies involve hospitals, not disappeared phones. Raise your standards and make 'basic communication skills' your new non-negotiable for dating.",
                    "This disappearing act is actually valuable information{user_name}. 🎯 It's showing you this person's character and communication style under pressure. Time to get brutal with yourself: Would you advise your best friend to chase someone who treats them as disposable? The answer is no. Set a clear deadline - I recommend 3 days max - and then consider it done. Grieve if needed, but don't wait around. Their ghosting has nothing to do with your worth and everything to do with their weakness. Use this as a filter - it's actually saved you time."
                ],
                'abandonment_event': [
                    "Ghosting you on your birthday reveals everything you need to know about their character and priorities{user_name}. 🔥 This isn't small or accidental - it's a direct statement about how little they respect you. Don't text them asking for explanations - that's beneath your dignity. Instead, take immediate action: 1) Block them on everything for at least two weeks, 2) Make new birthday plans with people who actually show up, 3) Write down this red flag so you never downplay it in the future. Anyone who can't even manage a birthday text doesn't deserve your time or attention.",
                    "Someone who disappears on your special day is showing you exactly where you stand{user_name}. 💪 Dead last in their priorities. This isn't a miscommunication - it's a deliberate choice that reflects their character. Here's your action plan: First, accept that this person doesn't have the emotional maturity for a real relationship. Second, establish a zero-tolerance policy for this kind of disrespect. Third, celebrate yourself anyway - don't let their absence dim your light. And finally, recognize that being alone is far better than being with someone who treats important moments as optional.",
                    "Let's be real{user_name} - disappearing on your birthday isn't an accident, it's a choice. 🎯 Someone who cares about you would NEVER do this, period. The standard you accept is the standard you'll receive, so make this decision right now: Are you willing to be someone's afterthought? Because that's what's happening. Don't send desperate texts or try to understand their side - there is no acceptable excuse. Block their number, tell a friend what happened so you stay accountable, and recognize this as the relationship-ending behavior it is."
                ]
            },
            'strategic': {
                'abandonment': [
                    "Let's analyze this ghosting situation objectively{user_name}. 🧠 The data clearly indicates a pattern of avoidance behavior that predicts future communication failures. Based on research, there's a 76% chance that someone who ghosts once will repeat this behavior. I recommend implementing a strategic response: 1) Establish a 72-hour waiting period with no contact attempts, 2) Document communication patterns before the ghosting to identify early warning signs, 3) Set concrete metrics for what constitutes acceptable communication going forward (such as response time, communication frequency, and conflict resolution approach). This evidence-based approach will protect you from investing in low-probability relationship outcomes.",
                    "Ghosting provides valuable data about communication styles and conflict avoidance{user_name}. 📊 Let's approach this systematically: First, conduct a retroactive analysis of the relationship timeline, identifying any previous instances of avoidant behavior or communication breakdown. Second, calculate the relationship investment ratio - were you putting in 80% of the effort? Third, implement a defined waiting period (5-7 days maximum) with clear exit criteria. After this period, proceed with the assumption that the relationship has terminated and redirect your emotional resources toward higher-probability connections.",
                    "From a strategic perspective, being ghosted requires a clear decision tree for your next steps{user_name}. 🎯 I recommend this structured approach: 1) Implement a strict no-pursuit policy for a minimum of 14 days, 2) During this time, objectively evaluate the relationship's communication patterns using specific metrics like reciprocity and consistency, 3) Set a firm boundary on what constitutes acceptable re-engagement (anything less than a clear explanation and concrete behavior change plan is insufficient), 4) Diversify your social connections to reduce dependency on unreliable communication partners. This approach maximizes your long-term relationship success probability."
                ],
                'abandonment_event': [
                    "Let's analyze the implications of someone disappearing on your special day{user_name}. 🧠 This behavior objectively demonstrates a critical flaw in their reliability framework and priority allocation system. The timing indicates a 94% probability that this is a pattern rather than an anomaly. My recommendation: 1) Implement immediate contact reduction, 2) Document this event in detail for future reference, 3) Establish a relationship assessment matrix that weighs reliability during significant events as a critical variable, 4) Set a firm 10-day evaluation period before making any decisions about continuing investment in this connection.",
                    "This birthday ghosting situation provides critical data points about how this person handles important occasions{user_name}. 📊 The evidence suggests a fundamental misalignment between their relationship behavior and standard expectation frameworks. Based on relationship success metrics, people who fail to acknowledge significant dates have a 68% higher chance of demonstrating unreliability in other critical relationship moments. Implement this action plan: 1) Conduct a thorough assessment of previous reliability instances, 2) Calculate the cost-benefit ratio of continued investment, 3) Develop specific, measurable criteria for what constitutes acceptable reliability before considering further engagement.",
                    "From a strategic perspective{user_name}, disappearing on significant dates like birthdays is a high-validity indicator of future behavior patterns. 🎯 This data point carries significant predictive weight about their future reliability. I recommend this evidence-based approach: 1) Implement a contact cooling period of 14-21 days, 2) During this time, objectively document all previous instances where they prioritized your needs versus their convenience, 3) Develop specific metrics for what constitutes acceptable relationship behavior, with special focus on reliability during significant occasions, 4) Set a clear decision threshold for continuation versus termination based on these objective criteria."
                ]
            },
            'intuitive': {
                'abandonment': [
                    "This ghosting experience, while painful, carries important soul wisdom for you{user_name}. ✨ The universe is creating necessary space in your life by removing someone who wasn't aligned with your authentic path. Trust this divine timing. I sense your soul is being prepared for a deeper connection that honors your true worth. Take these steps to align with this wisdom: First, perform a release ritual - write down what you're letting go of and burn it safely. Second, spend 10 minutes daily in meditation visualizing healing light filling the space they left. Third, pay attention to synchronicities and signs pointing you toward activities and people who truly value your essence.",
                    "When someone suddenly vanishes, it often creates space for something more aligned with your authentic path{user_name}. 🔮 This absence is actually a spiritual gift, though it doesn't feel that way now. The universe never removes something without making room for greater alignment. Here's your spiritual action plan: 1) Place your hand on your heart each morning and affirm 'I am divinely protected and guided,' 2) Notice what new energies or people enter your life in the next lunar cycle, 3) Release expectations about how healing should look and trust your inner wisdom to guide you toward soul-aligned connections who would never disappear without explanation.",
                    "There's a deeper spiritual meaning in this ghosting experience{user_name}. 🌙 This is a sacred threshold moment in your soul journey - the universe is breaking old attachment patterns to make way for more authentic connections. Your higher self orchestrated this experience to heal ancestral patterns of abandonment. I recommend these spiritual practices: 1) Each night before sleep, visualize cutting energetic cords to this person, 2) Keep a synchronicity journal noting meaningful coincidences that guide your next steps, 3) Create a self-love altar with objects representing your worth independent of others' validation."
                ],
                'abandonment_event': [
                    "Having someone disappear on your birthday carries a powerful symbolic meaning for your journey{user_name}. ✨ This experience is a spiritual initiation - the universe is teaching you to honor and celebrate yourself regardless of external validation. Your soul chose this birthday as the perfect time to release connections that don't mirror your true worth. Here's your spiritual guidance: 1) Create a personal rebirth ritual to reclaim this date as sacred to YOU, 2) Place crystals like rose quartz and amethyst around your living space to transmute abandonment energy, 3) For the next 7 days, write down three things you celebrate about yourself each morning. This birthday marks the beginning of profound self-reconnection.",
                    "This birthday abandonment, while deeply painful, is occurring at a spiritually significant time{user_name}. 🔮 The universe orchestrated this experience precisely when your soul was ready to break free from dependency on others for validation. Your guides are surrounding you with protective energy right now. Follow this intuitive guidance: 1) Light a candle and declare this as a rebirth moment rather than just a birthday, 2) Spend time in nature allowing Earth energy to ground and stabilize you, 3) Listen for intuitive nudges toward new connections that honor your authentic self. This experience is actually accelerating your spiritual awakening.",
                    "Special dates like birthdays carry powerful energetic significance{user_name}. 🌙 This abandonment is actually a cosmic reset button being pressed on your relationship patterns. The universe has removed this person on your soul's birthday to symbolize the end of an old chapter where you sought external validation. Your intuitive action steps are: 1) Create a self-blessing ceremony with elements representing earth, air, fire and water to honor your complete self, 2) Ask your guides each morning what gift you should give yourself today, 3) Trust that this painful experience is actually accelerating your soul's evolution toward authentic connections that never leave you questioning your worth."
                ]
            }
        }
        
        response_type = 'abandonment_event' if concern == 'abandonment_event' else 'abandonment'
        available_responses = abandonment_responses.get(coach_type, abandonment_responses['supportive']).get(response_type)
        
        if available_responses:
            response_template = random.choice(available_responses)
    
    # Personalize response with extracted information
    personalized_response = personalize_response(
        response_template, 
        user_message,
        user_name,
        situation_duration,
        emotion,
        relationship_status,
        concern,
        coach_type
    )
    
    return personalized_response

def generate_emotional_response(user_message, emotion, coach_type):
    """Generate a direct response to an emotional statement based on coach type"""
    
    # Responses specifically designed for emotion-focused messages
    emotional_responses = {
        'sad': {
            'supportive': [
                "I'm truly sorry you're feeling sad right now. Your emotions are valid and important. 💚 What's weighing on your heart today?",
                "It takes courage to acknowledge sadness. I'm here with you in this moment. 🤗 Would it help to share more about what's bringing you down?",
                "Thank you for sharing that you're feeling sad. You're not alone in this feeling. 💕 What kind of support would feel most helpful right now?"
            ],
            'direct': [
                "Sadness is telling you something important. 🔥 What specifically triggered these feelings, and what action do you need to take?",
                "Feeling sad is a signal, not a state to stay in. 💪 What's one step you can take today to address what's causing this?",
                "I hear you're sad. Let's not just sit in it - let's understand it and use it. 🎯 What is this sadness teaching you about your needs?"
            ],
            'strategic': [
                "I see you're experiencing sadness. Let's analyze this emotion systematically. 🧠 What patterns or triggers preceded this feeling?",
                "Sadness often indicates a gap between expectations and reality. 📊 Can you identify what specific expectation wasn't met?",
                "From a strategic perspective, your sadness is data. 🎯 What does this emotional response tell us about your core values and needs?"
            ],
            'intuitive': [
                "Your sadness carries wisdom if you listen deeply. ✨ What might your heart be trying to tell you through this feeling?",
                "Sadness often flows through us as a sacred river of release. 🔮 What might you be ready to let go of in this moment?",
                "This feeling of sadness is opening a doorway to deeper awareness. 🌙 What truth is emerging that perhaps you've been resisting?"
            ]
        },
        'anxious': {
            'supportive': [
                "I can hear the anxiety in your words, and I want you to know it's okay to feel this way. 💚 What's creating the most worry for you right now?",
                "Anxiety can feel so overwhelming, but you don't have to face it alone. 🤗 What specific concerns are at the forefront of your mind?",
                "I'm right here with you through these anxious feelings. 💕 What's one small thing we could focus on that might bring you some calm?"
            ],
            'direct': [
                "Anxiety thrives when we avoid facing things directly. 🔥 What specifically are you avoiding that's feeding this feeling?",
                "Let's cut through the anxiety and get to what's really happening. 💪 What's the worst-case scenario you're imagining?",
                "Anxiety is just fear in disguise. 🎯 Name exactly what you're afraid might happen so we can deal with it."
            ],
            'strategic': [
                "Anxiety can be approached systematically. 🧠 On a scale of 1-10, how would you rate it, and what specific scenarios are triggering it?",
                "Let's break down this anxiety into its component parts. 📊 What percentage is future worry versus present reality?",
                "Your anxiety represents uncertainty that can be strategically addressed. 🎯 What specific information would help reduce this uncertainty?"
            ],
            'intuitive': [
                "Anxiety often arises when we're disconnected from our inner knowing. ✨ What might happen if you placed a hand on your heart and took three deep breaths right now?",
                "Your anxiety holds important messages about alignment with your true path. 🔮 What aspect of your current situation feels out of alignment with your authentic self?",
                "This anxiety is an invitation to return to the present moment. 🌙 What is actually true right now, in this very moment of your existence?"
            ]
        },
        'confused': {
            'supportive': [
                "It's completely normal to feel confused when navigating relationships. 💚 What aspects feel most unclear to you right now?",
                "Confusion can be really uncomfortable, but it's also often part of finding clarity. 🤗 What possibilities are you considering?",
                "I hear that you're feeling confused, and that's a very valid response. 💕 What would help you feel more grounded as you work through this?"
            ],
            'direct': [
                "Confusion often comes from not wanting to face a clear reality. 🔥 What truth are you avoiding seeing?",
                "Let's cut through the confusion. What does your gut tell you when you remove all the overthinking? 💪",
                "Confusion is often just delaying a decision you already know you need to make. 🎯 What choice are you hesitating on?"
            ],
            'strategic': [
                "Confusion can be addressed by gathering the right data. 🧠 What specific information would help you make progress?",
                "Let's map out the sources of confusion systematically. 📊 What variables are unknown versus what facts are established?",
                "Strategic clarity comes from defined criteria. 🎯 What are your top three non-negotiables in this situation?"
            ],
            'intuitive': [
                "Confusion often clears when we quiet the mind and listen to the heart. ✨ If all external voices were silent, what would your inner wisdom say?",
                "This confusion is actually a powerful transitional state. 🔮 What old beliefs might you be outgrowing?",
                "Confusion is the threshold guardian between your old understanding and new wisdom. 🌙 What deeper knowing is trying to emerge?"
            ]
        },
        'angry': {
            'supportive': [
                "I hear how angry you're feeling, and that's completely valid. 💚 Would it help to share more about what's triggered these feelings?",
                "Anger often protects deeper emotions like hurt or fear. 🤗 What might be beneath this anger that feels vulnerable?",
                "Your anger deserves to be acknowledged. 💕 How can you honor this feeling while also taking care of yourself?"
            ],
            'direct': [
                "Anger is energy - the question is how you'll channel it. 🔥 What boundaries need to be established right now?",
                "Your anger is telling you something important about your limits. 💪 What specific action do you need to take?",
                "Let's use this anger productively. 🎯 What change is this feeling demanding in your situation?"
            ],
            'strategic': [
                "Anger can be analyzed for the valuable data it provides. 🧠 What specific triggers activated this response?",
                "Let's assess this anger objectively. 📊 On a scale of 1-10, how justified is this response to the situation?",
                "Strategic use of anger requires clear direction. 🎯 What specific outcome would resolve this emotion?"
            ],
            'intuitive': [
                "Your anger carries sacred fire and purpose. ✨ What truth is it illuminating that needs to be seen?",
                "This anger is a powerful messenger from your authentic self. 🔮 What boundary or value is being violated?",
                "When you listen deeply to this anger, what wisdom does it contain about your path forward? 🌙"
            ]
        }
    }
    
    # For emotions not explicitly mapped, use these defaults
    default_responses = {
        'supportive': [
            "Thank you for sharing how you're feeling. Your emotions are completely valid. 💚 Would you like to tell me more about what's happening?",
            "I appreciate you opening up about your feelings. 🤗 What support would be most helpful for you right now?",
            "I'm here with you in this emotion. 💕 How long have you been feeling this way?"
        ],
        'direct': [
            "I hear your emotion - now let's focus on what you're going to do about it. 🔥 What specific action do you need to take?",
            "Feelings are important signals, but they require action. 💪 What's your next step here?",
            "Let's use this emotion as fuel for change. 🎯 What specifically needs to change in your situation?"
        ],
        'strategic': [
            "Let's analyze what's behind this feeling. 🧠 What specific events triggered this emotional response?",
            "Your emotions provide important data. 📊 How would you rate the intensity, and what patterns do you notice?",
            "From a strategic perspective, what does this emotion tell us about your needs? 🎯"
        ],
        'intuitive': [
            "Your emotions are sacred messengers from your deeper self. ✨ What might this feeling be guiding you toward or away from?",
            "When you sit quietly with this feeling, what wisdom does it contain? 🔮",
            "This emotion is part of your soul's journey. 🌙 What might it be teaching you in this moment?"
        ]
    }
    
    # Get emotion-specific responses if available, otherwise use defaults
    emotion_specific_responses = emotional_responses.get(emotion)
    if emotion_specific_responses:
        responses = emotion_specific_responses.get(coach_type, emotion_specific_responses['supportive'])
    else:
        responses = default_responses.get(coach_type, default_responses['supportive'])
    
    # Select a response
    return random.choice(responses)

def personalize_response(template, user_message, user_name=None, duration=None, emotion=None, 
                        status=None, concern=None, coach_type='supportive'):
    """Personalize response template with specific details from user message"""
    # Create personalized elements to inject into template
    personalizations = {
        '{user_name}': user_name if user_name else '',
        '{duration}': f"in your {duration} relationship" if duration else '',
        '{emotion}': f"feeling {emotion}" if emotion else '',
        '{status}': status if status else 'relationship',
        '{concern}': concern if concern else 'situation'
    }
    
    # For abandonment/abandonment_event cases, just do simple substitution without adding anything else
    if concern in ['abandonment', 'abandonment_event']:
        # Only apply the direct substitutions to the template
        for marker, value in personalizations.items():
            template = template.replace(marker, value)
        # Return the template without adding any dynamic elements
        return template
    
    # For all other concerns, proceed with dynamic element generation
    dynamic_elements = []
    
    # Add emotion acknowledgment if detected
    if emotion:
        if coach_type == 'supportive':
            dynamic_elements.append(f"I can see you're feeling {emotion}, which is completely valid.")
        elif coach_type == 'direct':
            dynamic_elements.append(f"Your {emotion} feelings are trying to tell you something important.")
        elif coach_type == 'strategic':
            dynamic_elements.append(f"Objectively, this {emotion} response indicates a core need isn't being met.")
        elif coach_type == 'intuitive':
            dynamic_elements.append(f"The {emotion} energy you're experiencing has a deeper message for you.")
    
    # Add relationship status context if detected
    if status:
        status_descriptions = {
            'situationship': "undefined relationship",
            'dating': "dating situation",
            'exclusive': "committed relationship",
            'married': "marriage",
            'engaged': "engagement",
            'broken_up': "breakup situation",
            'long_distance': "long-distance relationship",
            'casual': "casual arrangement"
        }
        status_desc = status_descriptions.get(status, "relationship")
        
        if coach_type == 'supportive':
            dynamic_elements.append(f"In this {status_desc}, remember to honor your feelings.")
        elif coach_type == 'direct':
            dynamic_elements.append(f"Let's be real about what this {status_desc} actually is.")
        elif coach_type == 'strategic':
            dynamic_elements.append(f"When analyzing this {status_desc}, we need clear metrics.")
        elif coach_type == 'intuitive':
            dynamic_elements.append(f"This {status_desc} is teaching you important soul lessons.")
    
    # Add duration context if detected
    if duration:
        if coach_type == 'direct':
            dynamic_elements.append(f"After {duration}, you need to look at patterns, not promises.")
        elif coach_type == 'strategic':
            dynamic_elements.append(f"Given the {duration} timeframe, we can establish clear indicators.")
        
    # Add concern-specific elements
    if concern:
        concern_responses = {
            'communication': "Clear communication requires both participation and willingness.",
            'commitment': "Commitment isn't just a word - it's shown through consistent actions.",
            'trust': "Trust is rebuilt slowly, through repeated trustworthy actions over time.",
            'jealousy': "Jealousy often masks deeper insecurities that need compassionate attention.",
            'mixed_signals': "Mixed signals are actually clear signals of ambivalence or conflict.",
            'intimacy': "Intimacy flourishes in safety, not in uncertainty or pressure.",
            'moving_on': "Moving forward requires honoring the past while not living there.",
            'future': "Aligned futures require honest conversations about core values and desires.",
            'abandonment': "Being ghosted or suddenly abandoned is about their inability to communicate, not your worthiness.",
            'abandonment_event': "Having someone disappear on a special occasion like your birthday speaks to their character, not your value."
        }
        
        if concern in concern_responses:
            dynamic_elements.append(concern_responses[concern])
    
    # Add specific questions based on coach type - but not for abandonment cases
    if concern not in ['abandonment', 'abandonment_event']:
        questions = {
            'supportive': [
                "What would feel most nurturing for you right now?",
                "How can you honor your needs while still being compassionate with yourself?",
                "What does your heart truly want in this situation?"
            ],
            'direct': [
                "What's the action step you've been avoiding taking?",
                "When will you start enforcing this boundary?",
                "What standard are you no longer willing to compromise on?"
            ],
            'strategic': [
                "What specific outcome would indicate success to you?",
                "What's your timeline for making this decision?",
                "What data points would help clarify your next steps?"
            ],
            'intuitive': [
                "What is your intuition telling you that your mind might be resisting?",
                "What soul growth is being invited through this challenge?",
                "How might this situation be perfect for your spiritual evolution?"
            ]
        }
        
        question = random.choice(questions.get(coach_type, questions['supportive']))
        dynamic_elements.append(question)
    
    # Add personalization elements to template
    for marker, value in personalizations.items():
        template = template.replace(marker, value)
        
    # For abandonment responses, don't add dynamic elements - keep the concrete advice
    if concern in ['abandonment', 'abandonment_event']:
        return template
    
    # For other scenarios, add dynamic elements only if template seems generic
    if len(template) < 100 or "?" not in template:
        dynamic_content = " ".join(dynamic_elements)
        template = f"{template}\n\n{dynamic_content}"
    
    return template

def generate_fallback_response(user_message, coach_type):
    """Generate simple fallback responses if advanced fallback system fails"""
    
    fallback_responses = {
        'supportive': [
            "I hear you, and what you're sharing takes courage. Your feelings are completely valid. 💚 What feels like the most loving step you could take for yourself right now?",
            "Thank you for trusting me with this. It sounds like you're going through something really challenging. 🤗 How are you taking care of yourself through this?",
            "I can feel the emotion in your words. Remember that you deserve love, respect, and clarity in your relationships. ✨ What does your heart tell you?"
        ],
        'direct': [
            "Let's be real here - you already know what needs to happen. 🔥 Stop waiting for permission to trust your gut. What action are you avoiding?",
            "I hear a lot of excuses, but what I'm not hearing is you standing up for what you deserve. 💪 When are you going to start putting yourself first?",
            "Here's the truth: if someone wanted to be with you, they'd make it clear. 🎯 What are you going to do about this situation?"
        ],
        'strategic': [
            "Let's analyze this systematically. 🧠 What patterns do you notice in this situation? What data points indicate the relationship direction?",
            "Looking at this objectively, what are your non-negotiable requirements? 📊 How does the current situation measure against those standards?",
            "Strategic assessment needed here. 🎯 What's your timeline for clarity, and what specific actions will you take to achieve it?"
        ],
        'intuitive': [
            "Your soul is speaking to you through these feelings. ✨ What is your inner wisdom trying to tell you about this situation?",
            "Trust the energy you feel - it's rarely wrong. 🔮 What would love do in this situation? How can you honor your highest self?",
            "This challenge is asking you to step into your power. 🌙 What version of yourself wants to emerge from this experience?"
        ]
    }
    
    responses = fallback_responses.get(coach_type, fallback_responses['supportive'])
    return random.choice(responses)

# Advanced message analysis functions
def extract_name(user_message, conversation_history):
    """Extract user or partner name from message or conversation history"""
    name_indicators = [
        r"my name is (\w+)",
        r"I'm (\w+)",
        r"I am (\w+)",
        r"call me (\w+)"
    ]
    
    # Check current message
    for pattern in name_indicators:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # Check conversation history
    if conversation_history:
        for msg in conversation_history:
            if msg.get('type') == 'user':
                for pattern in name_indicators:
                    match = re.search(pattern, msg.get('message', ''), re.IGNORECASE)
                    if match:
                        return match.group(1)
    
    return None

def extract_duration(user_message):
    """Extract duration of relationship/situation from message"""
    duration_patterns = [
        r"(\d+)\s*years?",
        r"(\d+)\s*months?",
        r"(\d+)\s*weeks?",
        r"(\d+)\s*days?",
        r"a\s+few\s+(months|weeks|years)",
        r"couple\s+of\s+(months|weeks|years)",
        r"about\s+a\s+(month|week|year)"
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None

def extract_emotion(user_message):
    """Extract primary emotion from message with better context awareness"""
    emotion_keywords = {
        'angry': ['angry', 'mad', 'furious', 'frustrated', 'irritated', 'annoyed', 'rage', 'pissed'],
        'sad': ['sad', 'upset', 'unhappy', 'depressed', 'heartbroken', 'devastated', 'crying', 'down', 'blue', 'miserable', 'hurt'],
        'anxious': ['anxious', 'nervous', 'worried', 'stressed', 'overwhelmed', 'panicked', 'afraid', 'scared', 'fearful'],
        'confused': ['confused', 'unsure', 'uncertain', 'torn', 'indecisive', 'perplexed', 'lost', 'don\'t know', 'not sure'],
        'hurt': ['hurt', 'wounded', 'betrayed', 'abandoned', 'rejected', 'crushed', 'broken', 'pain'],
        'happy': ['happy', 'excited', 'hopeful', 'thrilled', 'optimistic', 'joyful', 'grateful', 'glad', 'good'],
        'jealous': ['jealous', 'envious', 'insecure', 'possessive'],
        'lonely': ['lonely', 'alone', 'isolated', 'empty', 'unloved', 'disconnected'],
        'guilty': ['guilty', 'shame', 'regret', 'remorse', 'sorry', 'apologetic']
    }
    
    # Check for direct emotion statements first (highest priority)
    direct_patterns = [
        r"i feel (\w+)",
        r"i am (\w+)",
        r"i'm (\w+)",
        r"i've been (\w+)",
        r"feeling (\w+)",
    ]
    
    user_message_lower = user_message.lower()
    
    # Check direct statements first
    for pattern in direct_patterns:
        matches = re.findall(pattern, user_message_lower)
        for match in matches:
            for emotion, keywords in emotion_keywords.items():
                if match in keywords:
                    return emotion
    
    # Then check for keyword mentions
    found_emotions = []
    emotion_weights = {
        'sad': 5,      # Prioritize sadness detection
        'hurt': 5,     # Prioritize hurt detection
        'anxious': 4,  # Medium-high priority
        'angry': 4,    # Medium-high priority
        'confused': 3, # Medium priority
        'lonely': 3,   # Medium priority
        'guilty': 2,   # Lower priority
        'jealous': 2,  # Lower priority
        'happy': 1     # Lowest priority (often mentioned in negation)
    }
    
    # Look for emotional keywords
    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in user_message_lower:
                # Check for negations
                negation_patterns = [
                    f"not {keyword}",
                    f"don't feel {keyword}",
                    f"doesn't make me {keyword}",
                    f"isn't {keyword}",
                    f"wasn't {keyword}"
                ]
                if not any(negation in user_message_lower for negation in negation_patterns):
                    # Calculate weight with priority and frequency
                    weight = emotion_weights.get(emotion, 1) * user_message_lower.count(keyword)
                    found_emotions.append((emotion, weight))
    
    if found_emotions:
        # Sort by weighted score and return most relevant
        found_emotions.sort(key=lambda x: x[1], reverse=True)
        return found_emotions[0][0]
    
    # Check for "need advice" pattern - typically indicates emotional distress
    if "need advice" in user_message_lower or "need help" in user_message_lower:
        return "anxious"
    
    # Default to sad for "not feeling good" patterns
    if "not feeling" in user_message_lower or "don't feel good" in user_message_lower:
        return "sad"
    
    return None

def extract_relationship_status(user_message):
    """Extract relationship status from message"""
    status_indicators = {
        'situationship': ['situationship', 'not defined', 'not official', 'unofficial', 'complicated'],
        'dating': ['dating', 'seeing each other', 'going out', 'been on dates'],
        'exclusive': ['exclusive', 'committed', 'monogamous', 'boyfriend', 'girlfriend'],
        'married': ['married', 'husband', 'wife', 'spouse'],
        'engaged': ['engaged', 'fiancé', 'fiancée'],
        'broken_up': ['ex', 'broke up', 'ended', 'dumped', 'left me'],
        'long_distance': ['long distance', 'ldr', 'different cities', 'miles away'],
        'casual': ['casual', 'friends with benefits', 'hookup', 'just physical']
    }
    
    user_message_lower = user_message.lower()
    
    for status, indicators in status_indicators.items():
        if any(indicator in user_message_lower for indicator in indicators):
            return status
    
    return None

def extract_main_concern(user_message):
    """Extract main relationship concern from message"""
    concern_indicators = {
        'communication': ['doesn\'t communicate', 'won\'t talk', 'stonewalling', 'communication issues', 'not answering', 'ignoring my texts'],
        'commitment': ['afraid of commitment', 'won\'t commit', 'commitment issues', 'afraid of labels'],
        'trust': ['trust issues', 'cheating', 'lying', 'suspicious', 'betrayed'],
        'jealousy': ['jealous', 'possessive', 'controlling', 'insecure'],
        'mixed_signals': ['mixed signals', 'hot and cold', 'confusing', 'unclear'],
        'intimacy': ['intimacy issues', 'physical connection', 'sex life', 'affection'],
        'moving_on': ['can\'t move on', 'still in love', 'get over', 'stuck'],
        'future': ['different goals', 'future plans', 'life goals', 'wants children'],
        'abandonment': ['disappeared', 'ghosted', 'stood up', 'didn\'t show up', 'left me', 'abandoned', 'no-show', 'vanished',
                      'stopped talking', 'went silent', 'not heard from', 'gone missing', 'no response', 'cut contact', 
                      'ignoring me', 'won\'t respond', 'isn\'t responding', 'doesn\'t respond', 'never showed up',
                      'suddenly stopped', 'stopped responding', 'cut all contact', 'won\'t reply']
    }
    
    user_message_lower = user_message.lower()
    
    # Get all relevant terms
    abandonment_terms = concern_indicators['abandonment']
    special_events = ['birthday', 'anniversary', 'holiday', 'christmas', 'valentine', 'graduation', 'wedding']
    negative_terms = ['missed', 'forgot', 'didn\'t come', 'wasn\'t there', 'didn\'t show', 'ruined', 'bad']
    
    # FIRST PRIORITY: Check for special events with abandonment (highest priority detection)
    for event in special_events:
        if event in user_message_lower:
            # If the message contains both the special event and any abandonment term
            if any(term in user_message_lower for term in abandonment_terms):
                logging.info(f"Detected special event abandonment: {event}")
                return 'abandonment_event'
            
            # Also check for negative terms with special events
            if any(term in user_message_lower for term in negative_terms):
                logging.info(f"Detected negative experience on special event: {event}")
                return 'abandonment_event'
    
    # SECOND PRIORITY: Regular abandonment detection if not a special event
    if any(term in user_message_lower for term in abandonment_terms):
        return 'abandonment'
        
    # Regular concern detection
    for concern, indicators in concern_indicators.items():
        if any(indicator in user_message_lower for indicator in indicators):
            return concern
    
    return None

def store_ai_conversation(customer_id, coach_type, user_message, ai_response):
    """Store AI conversation in database for history and analytics"""
    try:
        conn = sqlite3.connect('oracle.db')
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_coach_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                coach_type TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT
            )
        ''')
        
        # Insert conversation
        cursor.execute('''
            INSERT INTO ai_coach_conversations 
            (customer_id, coach_type, user_message, ai_response, session_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (customer_id, coach_type, user_message, ai_response, session.get('session_id', str(uuid.uuid4()))))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logging.error(f"Database error storing conversation: {str(e)}")

@app.route('/test-abandonment', methods=['GET'])
def test_abandonment_responses():
    """Test endpoint for abandonment responses"""
    test_message = "hey, i need advice, my boyfriend just disappeared on my birthday"
    
    concern = extract_main_concern(test_message)
    emotion = extract_emotion(test_message)
    
    responses = {}
    for coach_type in ["supportive", "direct", "strategic", "intuitive"]:
        response = generate_advanced_fallback_response(test_message, coach_type, [])
        responses[coach_type] = response
    
    # Add diagnostics
    responses['diagnostics'] = {
        'concern': concern,
        'emotion': emotion
    }
    
    return jsonify(responses)

@app.route('/ai-coach/history')
def ai_coach_history():
    """Get user's AI coach conversation history"""
    if 'customer_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        conn = sqlite3.connect('oracle.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT coach_type, user_message, ai_response, timestamp 
            FROM ai_coach_conversations 
            WHERE customer_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''', (session['customer_id'],))
        
        conversations = cursor.fetchall()
        conn.close()
        
        history = []
        for conv in conversations:
            history.append({
                'coach_type': conv[0],
                'user_message': conv[1],
                'ai_response': conv[2],
                'timestamp': conv[3]
            })
        
        return jsonify({'history': history})
        
    except Exception as e:
        logging.error(f"Error fetching conversation history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

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


# --- Custom Ritual Session Route ---
@app.route('/ritual-session', methods=['POST'])
def ritual_session():
    # Collect form data
    data = {
        'birthday': request.form.get('birthday'),
        'mood': request.form.get('mood'),
        'environment': request.form.get('environment'),
        'duration': int(request.form.get('duration', 5)),  # ensure int
        'time_of_day': request.form.get('time_of_day'),
        'ritual_need': request.form.get('ritual_need'),
        'movement_type': request.form.get('movement_type'),
        'body_areas': request.form.getlist('body_areas'),
        'breathing_style': request.form.get('breathing_style'),
        'intensity_level': request.form.get('intensity_level'),
        'ritual_items': request.form.getlist('ritual_items'),
    }

    # Generate ritual steps as dicts with title and instruction
    steps = []
    # Example logic: personalize steps based on need, movement, and mood
    if data['ritual_need'] == 'energy':
        steps.append({'title': 'Energizing Breathwork', 'instruction': 'Start with 2 minutes of deep, energizing breaths.'})
        steps.append({'title': 'Dynamic Warm-up', 'instruction': 'Do a quick dynamic warm-up to activate your body.'})
    elif data['ritual_need'] == 'grounding':
        steps.append({'title': 'Grounding Breath', 'instruction': 'Begin with slow, mindful breathing to center yourself.'})
        steps.append({'title': 'Restorative Yoga', 'instruction': 'Practice restorative yoga or gentle stretching.'})
    elif data['ritual_need'] == 'peace':
        steps.append({'title': 'Calming Breathwork', 'instruction': 'Begin with a calming breathwork session.'})
        steps.append({'title': 'Stillness', 'instruction': 'Sit in stillness or meditate for a few minutes.'})
    elif data['ritual_need'] == 'clarity':
        steps.append({'title': 'Focused Breathing', 'instruction': 'Start with focused breathing and set an intention.'})
        steps.append({'title': 'Mindful Walking', 'instruction': 'Do a mindful walking or journaling exercise.'})
    elif data['ritual_need'] == 'confidence':
        steps.append({'title': 'Power Poses', 'instruction': 'Begin with power poses and affirmations.'})
        steps.append({'title': 'Dynamic Flow', 'instruction': 'Move through a dynamic flow or light exercise.'})
    elif data['ritual_need'] == 'healing':
        steps.append({'title': 'Gentle Breathwork', 'instruction': 'Start with gentle breathwork and self-compassion.'})
        steps.append({'title': 'Restorative Movement', 'instruction': 'Focus on restorative movement and body awareness.'})
    else:
        steps.append({'title': 'Mindful Breathing', 'instruction': 'Begin with mindful breathing.'})
        steps.append({'title': 'Gentle Movement', 'instruction': 'Move gently and listen to your body.'})

    # Add movement type
    if data['movement_type'] == 'dynamic_flow':
        steps.append({'title': 'Dynamic Flow', 'instruction': 'Follow a dynamic flow sequence for 5-10 minutes.'})
    elif data['movement_type'] == 'restorative_yoga':
        steps.append({'title': 'Restorative Yoga', 'instruction': 'Hold restorative yoga poses for 2-3 minutes each.'})
    elif data['movement_type'] == 'therapeutic_stretching':
        steps.append({'title': 'Therapeutic Stretching', 'instruction': 'Do targeted therapeutic stretches for your selected areas.'})
    elif data['movement_type'] == 'mindful_walking':
        steps.append({'title': 'Mindful Walking', 'instruction': 'Take a mindful walk, focusing on each step and breath.'})
    elif data['movement_type'] == 'advanced_breathwork':
        steps.append({'title': 'Advanced Breathwork', 'instruction': 'Practice advanced breathwork techniques for 5 minutes.'})
    elif data['movement_type'] == 'deep_stillness':
        steps.append({'title': 'Deep Stillness', 'instruction': 'Sit or lie in deep stillness, focusing on relaxation.'})

    # Add body area focus
    if data['body_areas']:
        area_map = {
            'neck_shoulders': 'neck and shoulders',
            'spine_back': 'spine and back',
            'hips_pelvis': 'hips and pelvis',
            'legs_feet': 'legs and feet',
            'arms_hands': 'arms and hands',
            'jaw_face': 'jaw and face',
        }
        focus_areas = [area_map.get(a, a) for a in data['body_areas']]
        steps.append({'title': 'Body Focus', 'instruction': f'Pay special attention to: {", ".join(focus_areas)}.'})

    # Add a closing step
    steps.append({'title': 'Closing', 'instruction': 'End your ritual with gratitude and a few deep breaths.'})

    return render_template('ritual-session.html', ritual_data=data, ritual_steps=steps)

# Run the application
if __name__ == '__main__':
    # Initialize the database
    init_db()
    print("🚀 Starting Oracle Platform on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
