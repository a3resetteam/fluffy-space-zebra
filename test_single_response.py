import sys
import os

# Import the functions from app.py
from app import generate_advanced_fallback_response

def test_one_response():
    message = "hey, i need advice, my boyfriend just disappeared on my birthday"
    coach_type = "direct"
    response = generate_advanced_fallback_response(message, coach_type, [])
    
    # Write to file
    with open("single_response.txt", "w") as f:
        f.write(f"DIRECT COACH RESPONSE:\n{response}")
    
    print("Test completed and written to single_response.txt")

if __name__ == "__main__":
    test_one_response()
