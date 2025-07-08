#!/usr/bin/env python3
"""
Minimal test to check if we can start Flask
"""

import sys
import os
sys.path.insert(0, '/workspaces/codespaces-blank')

print("Python version:", sys.version)
print("Working directory:", os.getcwd())

try:
    from flask import Flask
    print("✓ Flask import successful")
except Exception as e:
    print("✗ Flask import failed:", e)
    sys.exit(1)

try:
    import sqlite3
    print("✓ SQLite import successful")
except Exception as e:
    print("✗ SQLite import failed:", e)

try:
    import stripe
    print("✓ Stripe import successful")
except Exception as e:
    print("✗ Stripe import failed:", e)

try:
    import openai
    print("✓ OpenAI import successful")
except Exception as e:
    print("✗ OpenAI import failed:", e)

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv import successful")
except Exception as e:
    print("✗ python-dotenv import failed:", e)

# Test basic Flask app
print("\nTesting basic Flask app...")
app = Flask(__name__)

@app.route('/')
def hello():
    return "Oracle Platform Test - Flask is working!"

if __name__ == '__main__':
    print("Starting test Flask app on http://0.0.0.0:5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)
