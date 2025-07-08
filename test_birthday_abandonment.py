import requests
import json
import random
import string

def generate_random_string(length=10):
    """Generate a random string for testing"""
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Base URL for the Flask app
BASE_URL = "http://localhost:5000"

# Test user credentials - Use a known existing user
test_email = "user@example.com"
test_password = "password"

# Skip user creation as we're using an existing user
def create_test_user():
    print("Using existing test user account")
    return True

# Login with test user
def login():
    response = requests.post(
        f"{BASE_URL}/login", 
        json={
            "email": test_email,
            "password": test_password
        }
    )
    print(f"Login response: {response.status_code}")
    return response.cookies if response.status_code == 200 else None

# Test AI coach with birthday ghosting scenario
def test_ai_coach_birthday_ghosting(cookies, coach_type="supportive"):
    test_message = "I'm really upset because my boyfriend ghosted me on my birthday. He was supposed to take me out to dinner but he never showed up and now he won't respond to any of my texts. It's been 3 days and I'm heartbroken."
    
    response = requests.post(
        f"{BASE_URL}/ai-coach/chat",
        json={
            "message": test_message,
            "coach_type": coach_type,
            "conversation_history": []
        },
        cookies=cookies
    )
    
    print(f"AI coach response status: {response.status_code}")
    
    if response.status_code == 200:
        response_data = response.json()
        print(f"\nCoach Type: {coach_type}")
        print(f"Response: {response_data.get('response')}")
        return response_data
    else:
        print(f"Error: {response.text}")
        return None

# Main test function
def main():
    print("Creating test user...")
    if create_test_user():
        print("Successfully created test user")
        
        print("Logging in...")
        cookies = login()
        
        if cookies:
            print("Successfully logged in")
            
            # Test with different coach types
            coach_types = ["supportive", "direct", "strategic", "intuitive"]
            
            for coach_type in coach_types:
                print(f"\nTesting {coach_type} coach with birthday ghosting scenario...")
                test_ai_coach_birthday_ghosting(cookies, coach_type)
                
            print("\nTests completed!")
        else:
            print("Failed to login")
    else:
        print("Failed to create test user")

if __name__ == "__main__":
    main()
