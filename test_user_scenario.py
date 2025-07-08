import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the functions from app.py
from app import extract_main_concern, extract_emotion, generate_advanced_fallback_response

def test_user_exact_scenario():
    """Test the exact scenario provided by the user"""
    
    # The exact scenario from the user
    message = "hey, i need advice, my boyfriend just disappeared on my birthday"
    
    print("\n===== TESTING USER SCENARIO =====\n")
    
    # Check concern detection
    concern = extract_main_concern(message)
    emotion = extract_emotion(message)
    
    print(f"Message: '{message}'")
    print(f"Detected Concern: {concern}")
    print(f"Detected Emotion: {emotion}")
    
    # Test all coach types
    for coach_type in ["supportive", "direct", "strategic", "intuitive"]:
        response = generate_advanced_fallback_response(message, coach_type, [])
        
        print(f"\n{coach_type.upper()} COACH RESPONSE:")
        print(f"{response}")
        print("-" * 80)

if __name__ == "__main__":
    test_user_exact_scenario()
