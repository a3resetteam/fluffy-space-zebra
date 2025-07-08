import sys
import os
import re
import sqlite3
import logging
import random

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the functions from app.py
from app import extract_main_concern, extract_emotion

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_birthday_extraction():
    """Test specifically for birthday abandonment detection"""
    
    test_cases = [
        "my boyfriend just disappeared on my birthday",
        "I need advice, my boyfriend just disappeared on my birthday",
        "Hey, I need help, my boyfriend ghosted me on my birthday",
        "I'm really upset because my boyfriend ghosted me on my birthday",
        "We were supposed to celebrate my birthday but he never showed up",
        "She forgot my birthday and now isn't responding to my texts",
        "I got stood up on my birthday by my girlfriend"
    ]
    
    print("\n===== TESTING BIRTHDAY ABANDONMENT DETECTION =====\n")
    
    for i, message in enumerate(test_cases):
        print(f"\nTest Case {i+1}: '{message}'")
        
        # Test extraction function
        concern = extract_main_concern(message)
        
        print(f"Detected Concern: {concern}")
        
        if concern == 'abandonment_event':
            print("✅ SUCCESS: Correctly detected as abandonment_event")
        else:
            print("❌ FAILED: Should be detected as abandonment_event")
        
        print("-" * 50)

if __name__ == "__main__":
    test_birthday_extraction()
