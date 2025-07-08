#!/usr/bin/env python3
"""
Create a simple test page to debug ritual display
"""

from flask import Flask, render_template

app = Flask(__name__)

# Sample ritual data for testing
sample_ritual_data = {
    'title': 'Test Restorative Yoga Ritual',
    'duration': 15,
    'intensity': 'gentle_restoration',
    'breathing_style': 'calming_breath',
    'total_steps': 4,
    'focus_areas': ['neck_shoulders', 'spine_back'],
    'steps': [
        {
            'phase': 'Opening',
            'duration': 2,
            'emoji': '🌅',
            'title': 'Sacred Space Creation',
            'instructions': [
                '🕯️ Light candles or set intention',
                '🧘‍♀️ Take 3 deep breaths to arrive',
                '💫 Set clear intention for your practice'
            ]
        },
        {
            'phase': 'Breath Work',
            'duration': 3,
            'emoji': '🌬️',
            'title': '4-7-8 Calming Breath',
            'instructions': [
                '💨 Inhale through nose for 4 counts',
                '🫁 Hold breath gently for 7 counts',
                '🌬️ Exhale through mouth for 8 counts'
            ],
            'benefits': 'Activates parasympathetic nervous system, reduces anxiety'
        },
        {
            'phase': 'Movement',
            'duration': 8,
            'emoji': '💃',
            'title': 'Restorative Yoga Sequence',
            'instructions': [
                '🕊️ Supported fish pose (3 minutes)',
                '😌 Gentle neck massage (2 minutes)',
                '🌸 Shoulder melting at wall (3 minutes)'
            ],
            'focus_areas': ['neck_shoulders', 'spine_back']
        },
        {
            'phase': 'Integration',
            'duration': 2,
            'emoji': '✨',
            'title': 'Sacred Integration',
            'instructions': [
                '🧘‍♀️ Sit in comfortable stillness',
                '💫 Feel the effects of your practice',
                '🙏 Express gratitude for your body'
            ]
        }
    ]
}

@app.route('/test-ritual')
def test_ritual():
    return render_template('ritual-session.html', 
                         ritual_data=sample_ritual_data,
                         ritual_steps=sample_ritual_data['steps'],
                         form_data={},
                         progress={'completion_percentage': 0})

if __name__ == '__main__':
    print("🧪 Starting test app at http://localhost:5003/test-ritual")
    app.run(debug=True, host='0.0.0.0', port=5003)
