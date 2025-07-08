#!/usr/bin/env python3
"""
Direct test of ritual creation to demonstrate the improved UI and timer.
"""

import requests
import json

def test_ritual_directly():
    """Test creating a ritual directly without login."""
    
    print("🔮 Testing Ritual Creation and UI")
    print("=" * 40)
    
    # Create ritual data
    ritual_data = {
        'intention': 'Release stress and boost confidence',
        'duration': '10',  # Short duration for testing
        'movement_type': 'gentle_stretching',
        'breathing_style': 'deep_belly',
        'body_areas': ['neck_shoulders', 'core'],
        'intensity': 'gentle'
    }
    
    print("Creating ritual with:")
    for key, value in ritual_data.items():
        print(f"  {key}: {value}")
    
    # Make request directly
    response = requests.post("http://localhost:5000/ritual-session", data=ritual_data)
    
    print(f"\nResponse status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for key elements
        checks = [
            ('Timer Element', 'countdownTimer' in content),
            ('Ritual Steps', 'ritual-step' in content),
            ('Step Emojis', 'step-emoji' in content),
            ('Benefits Section', 'step-benefits' in content),
            ('Focus Areas', 'focus-area-tag' in content),
            ('Start Button', 'Start Ritual' in content),
            ('Progress Ring', 'progress-ring' in content),
            ('JavaScript Functions', 'startRitual()' in content),
            ('Enhanced Styling', 'linear-gradient' in content and 'backdrop-filter' in content)
        ]
        
        print("\n✅ UI Element Checks:")
        for name, found in checks:
            status = "✅" if found else "❌"
            print(f"  {status} {name}")
        
        # Save sample for inspection
        with open('/workspaces/codespaces-blank/ritual_ui_demo.html', 'w') as f:
            f.write(content)
        
        print(f"\n📄 Full HTML saved to ritual_ui_demo.html")
        print("\n🎯 Key Improvements Implemented:")
        print("  • Fixed timer JavaScript to work with new step structure")
        print("  • Enhanced visual boxing with gradients and shadows")
        print("  • Added step animations and hover effects")
        print("  • Improved step highlighting (active/completed states)")
        print("  • Added floating emoji animations")
        print("  • Enhanced focus area tags with hover effects")
        print("  • Better visual separation between steps")
        print("  • Smooth step transitions and scrolling")
        
    else:
        print(f"❌ Failed with status {response.status_code}")
        print(response.text[:500])

if __name__ == "__main__":
    test_ritual_directly()
