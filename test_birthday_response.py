import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the functions from app.py
from app import extract_main_concern, extract_emotion, generate_advanced_fallback_response

def test_birthday_abandonment_responses():
    """Test responses for birthday abandonment scenarios"""
    
    message = "I need advice, my boyfriend just disappeared on my birthday"
    
    print("\n===== TESTING BIRTHDAY ABANDONMENT RESPONSES =====\n")
    
    # Check concern detection
    concern = extract_main_concern(message)
    print(f"Detected Concern: {concern}")
    
    # Test responses for different coach types
    for coach_type in ["supportive", "direct", "strategic", "intuitive"]:
        response = generate_advanced_fallback_response(message, coach_type, [])
        print(f"\n{coach_type.title()} Coach Response:")
        print(f"{response}")
        print("-" * 80)

if __name__ == "__main__":
    test_birthday_abandonment_responses()
