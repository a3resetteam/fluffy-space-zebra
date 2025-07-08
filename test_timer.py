#!/usr/bin/env python3

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Sample ritual data for testing timer
sample_ritual_data = {
    "title": "🌟 Quick Timer Test Ritual",
    "duration": 2,  # Short duration for testing
    "intensity": "gentle",
    "breathing_style": "box_breathing",
    "total_steps": 2,
    "focus_areas": ["mindfulness", "breathing"],
    "steps": [
        {
            "title": "Center Yourself",
            "phase": "preparation",
            "duration": 1,  # 1 minute for testing
            "emoji": "🧘‍♀️",
            "instructions": [
                "Find a comfortable seated position",
                "Close your eyes gently",
                "Take three deep breaths"
            ],
            "benefits": "Creates mental clarity and presence",
            "focus_areas": ["mindfulness", "breathing"]
        },
        {
            "title": "Breathe with Intention",
            "phase": "action",
            "duration": 1,  # 1 minute for testing
            "emoji": "🌬️", 
            "instructions": [
                "Inhale for 4 counts",
                "Hold for 4 counts",
                "Exhale for 4 counts",
                "Hold empty for 4 counts"
            ],
            "benefits": "Reduces stress and activates calm focus",
            "focus_areas": ["breathing", "stress_relief"]
        }
    ]
}

@app.route('/timer-test')
def timer_test():
    """Test page for timer functionality with a short ritual"""
    return render_template('ritual-session.html', 
                         ritual_data=sample_ritual_data,
                         ritual_steps=sample_ritual_data['steps'],
                         form_data={},
                         progress={'completion_percentage': 0})

if __name__ == '__main__':
    print("⏰ Starting timer test app at http://localhost:5004/timer-test")
    print("This ritual has a 2-minute duration for quick testing!")
    app.run(debug=True, host='0.0.0.0', port=5004)
