#!/usr/bin/env python3
"""Test script to check imports"""

try:
    print("Testing basic imports...")
    import os
    print("✓ os imported")
    
    import sqlite3
    print("✓ sqlite3 imported")
    
    import json
    print("✓ json imported")
    
    from flask import Flask
    print("✓ Flask imported")
    
    from dotenv import load_dotenv
    print("✓ python-dotenv imported")
    
    import openai
    print("✓ openai imported")
    
    print("\nAll imports successful!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
