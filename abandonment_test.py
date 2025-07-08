#!/usr/bin/env python3
import sys
import os
import json

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app.py functions
from app import extract_main_concern, extract_emotion, generate_advanced_fallback_response

def test_abandonment_responses():
    test_message = "hey, i need advice, my boyfriend just disappeared on my birthday"
    concern = extract_main_concern(test_message)
    emotion = extract_emotion(test_message)
    
    print(f"Message: {test_message}")
    print(f"Concern: {concern}")
    print(f"Emotion: {emotion}")
    
    # Get responses for each coach type
    results = {}
    for coach_type in ["supportive", "direct", "strategic", "intuitive"]:
        response = generate_advanced_fallback_response(test_message, coach_type, [])
        results[coach_type] = response
        print(f"\n{coach_type.upper()} RESPONSE:")
        print(response)
        print("-" * 80)
    
    # Save to file
    with open("abandonment_responses.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("Results saved to abandonment_responses.json")

if __name__ == "__main__":
    test_abandonment_responses()
