import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the functions from app.py
from app import extract_main_concern, extract_emotion, generate_advanced_fallback_response

def test_enhanced_responses():
    """Test the enhanced responses for abandonment scenarios"""
    
    test_cases = [
        "hey, i need advice, my boyfriend just disappeared on my birthday",
        "my girlfriend ghosted me after we dated for 3 months",
        "my husband isn't responding to my texts for the last week"
    ]
    
    coach_types = ["supportive", "direct", "strategic", "intuitive"]
    
    print("\n===== TESTING ENHANCED RESPONSES =====\n")
    
    for i, message in enumerate(test_cases):
        print(f"\n===== TEST CASE {i+1}: '{message}' =====\n")
        
        # Check concern detection
        concern = extract_main_concern(message)
        emotion = extract_emotion(message)
        
        print(f"Detected Concern: {concern}")
        print(f"Detected Emotion: {emotion}")
        
        # Test all coach types
        for coach_type in coach_types:
            response = generate_advanced_fallback_response(message, coach_type, [])
            
            print(f"\n{coach_type.upper()} COACH RESPONSE:")
            print(f"{response}")
            print("-" * 80)

if __name__ == "__main__":
    test_enhanced_responses()
