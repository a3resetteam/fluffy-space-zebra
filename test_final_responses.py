import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.FileHandler("test_output.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Import the functions from app.py
from app import extract_main_concern, extract_emotion, generate_advanced_fallback_response

def test_final_responses():
    """Test the final updated responses to ensure they're concrete and without generic additions"""
    
    # Write results to a file
    with open("response_test_results.txt", "w") as f:
        # The exact scenario from the user
        message = "hey, i need advice, my boyfriend just disappeared on my birthday"
        
        f.write("\n===== TESTING FINAL RESPONSES =====\n\n")
        
        # Check concern detection
        concern = extract_main_concern(message)
        emotion = extract_emotion(message)
        
        f.write(f"Message: '{message}'\n")
        f.write(f"Detected Concern: {concern}\n")
        f.write(f"Detected Emotion: {emotion}\n")
        
        # Test all coach types
        for coach_type in ["supportive", "direct", "strategic", "intuitive"]:
            response = generate_advanced_fallback_response(message, coach_type, [])
            
            f.write(f"\n{coach_type.upper()} COACH RESPONSE:\n")
            f.write(f"{response}\n")
            f.write("-" * 80 + "\n")
        
    logger.info("Test completed. Results written to response_test_results.txt")
    
if __name__ == "__main__":
    test_final_responses()
