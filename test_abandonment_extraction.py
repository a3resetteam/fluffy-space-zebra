import sys
import os
import re
import sqlite3
import logging
import random

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the functions from app.py
from app import extract_main_concern, extract_emotion, generate_advanced_fallback_response

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_extraction_functions():
    """Test the extraction functions with various abandonment scenarios"""
    
    test_cases = [
        "I'm really upset because my boyfriend ghosted me on my birthday. He was supposed to take me out to dinner but he never showed up and now he won't respond to any of my texts.",
        "My girlfriend completely disappeared on me the day before our anniversary. No explanation, no texts, nothing.",
        "I got all dressed up for our Valentine's Day date and they just never showed up. It's been a week and still no response.",
        "I can't believe he ghosted me right after my graduation ceremony. I thought he cared about me.",
        "We were supposed to meet for Christmas dinner with my family and she just vanished. No call, no text, nothing.",
        "I've been dating this guy for 3 months and he suddenly stopped responding to my texts last week.",
        "My partner of 2 years suddenly cut all contact with me without any explanation."
    ]
    
    print("\n===== TESTING EXTRACTION FUNCTIONS =====\n")
    
    for i, message in enumerate(test_cases):
        print(f"\nTest Case {i+1}: '{message[:50]}...'")
        
        # Test extraction functions
        concern = extract_main_concern(message)
        emotion = extract_emotion(message)
        
        print(f"Detected Concern: {concern}")
        print(f"Detected Emotion: {emotion}")
        
        # Test fallback response generation
        for coach_type in ["supportive", "direct", "strategic", "intuitive"]:
            response = generate_advanced_fallback_response(message, coach_type, [])
            print(f"\n{coach_type.title()} Coach Response:")
            print(f"{response[:100]}...\n")
        
        print("-" * 50)

if __name__ == "__main__":
    test_extraction_functions()
