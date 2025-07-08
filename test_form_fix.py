#!/usr/bin/env python3
"""
Test the ritual creator form with minimal required fields.
"""

import requests

def test_minimal_form():
    """Test form with only required fields filled."""
    
    print("🧪 Testing Ritual Creator Form with Minimal Fields")
    print("=" * 55)
    
    # Minimal required data
    minimal_data = {
        'duration': '15',
        'movement_type': 'therapeutic_stretching',
        'breathing_style': 'deep_healing',
        'intensity_level': 'moderate_activation'
    }
    
    print("Submitting form with minimal required fields:")
    for key, value in minimal_data.items():
        print(f"  {key}: {value}")
    
    try:
        response = requests.post("http://localhost:5000/ritual-session", 
                               data=minimal_data, 
                               timeout=10)
        
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Form submission successful!")
            
            # Quick content checks
            content = response.text
            checks = [
                ('Ritual session page loaded', '<title>' in content and 'Ritual Session' in content),
                ('Steps generated', 'ritual-step' in content),
                ('Timer present', 'countdownTimer' in content),
                ('Therapeutic content', 'therapeutic' in content.lower() or 'fascial' in content.lower())
            ]
            
            print("\n📋 Content Checks:")
            for name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"  {status} {name}")
                
        elif response.status_code == 302:
            print("🔄 Form redirected (possibly to login)")
            print(f"Redirect location: {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"❌ Form submission failed")
            print(f"Response: {response.text[:300]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        
    print("\n🎯 If this works, the 'Create My Ritual' button should now function properly!")

if __name__ == "__main__":
    test_minimal_form()
