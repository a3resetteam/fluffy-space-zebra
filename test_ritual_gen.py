#!/usr/bin/env python3
"""
Test the ritual generation function directly
"""

import sys
sys.path.append('.')

from app import generate_intelligent_ritual
import json

# Test data
test_form_data = {
    'birthday': '1990-01-01',
    'mood': 'calm',
    'environment': 'indoor',
    'duration': '15',
    'time_of_day': 'morning',
    'ritual_need': 'peace',
    'movement_type': 'restorative_yoga',
    'body_areas': ['neck_shoulders', 'spine_back'],
    'breathing_style': 'calming_breath',
    'intensity_level': 'gentle_restoration',
    'ritual_items': ['candles'],
    'elemental_focus': 'water',
    'focus_area': 'mindfulness'
}

print("🧪 Testing ritual generation function...")

try:
    ritual_data = generate_intelligent_ritual(test_form_data)
    print("✅ Ritual generated successfully!")
    print(f"📋 Title: {ritual_data['title']}")
    print(f"⏱️ Duration: {ritual_data['duration']} minutes")
    print(f"📊 Total Steps: {ritual_data['total_steps']}")
    print(f"🎯 Focus Areas: {ritual_data['focus_areas']}")
    
    print("\n🔍 Generated Steps:")
    for i, step in enumerate(ritual_data['steps'], 1):
        print(f"  {i}. {step['emoji']} {step['title']} ({step['duration']} min)")
        print(f"     Phase: {step['phase']}")
        print(f"     Instructions: {len(step['instructions'])} items")
        if 'benefits' in step:
            print(f"     Benefits: {step['benefits'][:50]}...")
        print()
    
    # Test JSON serialization
    json_data = json.dumps(ritual_data, indent=2)
    print("✅ JSON serialization successful")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
