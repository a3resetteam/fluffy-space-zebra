import requests
import json
import time

def test_abandonment_api():
    """Test the abandonment responses through the API endpoint"""
    base_url = "http://localhost:5000"
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    try:
        # Test the abandonment endpoint
        response = requests.get(f"{base_url}/test-abandonment")
        
        if response.status_code == 200:
            data = response.json()
            
            print("API TEST RESULTS:")
            print(f"Concern detected: {data['diagnostics']['concern']}")
            print(f"Emotion detected: {data['diagnostics']['emotion']}")
            
            # Print each coach response
            for coach_type, coach_response in data.items():
                if coach_type != 'diagnostics':
                    print(f"\n{coach_type.upper()} COACH RESPONSE:")
                    print(coach_response)
                    print("-" * 80)
            
            # Save responses to file
            with open("api_test_responses.json", "w") as f:
                json.dump(data, f, indent=2)
                
            print("\nResponses saved to api_test_responses.json")
        else:
            print(f"API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error testing API: {str(e)}")

if __name__ == "__main__":
    test_abandonment_api()
