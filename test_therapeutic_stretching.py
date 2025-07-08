#!/usr/bin/env python3
"""
Test therapeutic stretching sequence to verify detailed instructions.
"""

import requests
import json

def test_therapeutic_stretching():
    """Test creating a ritual with therapeutic stretching."""
    
    print("🎯 Testing Therapeutic Stretching Sequence")
    print("=" * 50)
    
    # Create ritual data with therapeutic stretching
    ritual_data = {
        'intention': 'Therapeutic muscle tension release',
        'duration': '20',
        'movement_type': 'therapeutic_stretching',
        'breathing_style': 'deep_healing',
        'body_areas': ['neck_shoulders', 'spine_back', 'hips_pelvis'],
        'intensity': 'gentle'
    }
    
    print("Testing therapeutic stretching with:")
    for key, value in ritual_data.items():
        print(f"  {key}: {value}")
    
    # Make request
    response = requests.post("http://localhost:5000/ritual-session", data=ritual_data)
    
    print(f"\nResponse status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for therapeutic stretching specific content
        therapeutic_keywords = [
            'fascial release',
            'trigger points', 
            'neural gliding',
            'contract-relax',
            'myofascial',
            'therapeutic'
        ]
        
        print("\n✅ Therapeutic Stretching Content Checks:")
        for keyword in therapeutic_keywords:
            found = keyword.lower() in content.lower()
            status = "✅" if found else "❌"
            print(f"  {status} Contains '{keyword}': {found}")
        
        # Check for proper instructions structure
        instruction_checks = [
            ('Detailed Instructions', 'hold' in content.lower() and 'seconds' in content.lower()),
            ('Step Duration', 'minutes' in content.lower()),
            ('Specific Techniques', '🎯' in content or '💆‍♀️' in content),
            ('Body Area Targeting', any(area in content.lower() for area in ['neck', 'shoulders', 'spine', 'hips']))
        ]
        
        print("\n📋 Instruction Quality Checks:")
        for name, found in instruction_checks:
            status = "✅" if found else "❌"
            print(f"  {status} {name}: {found}")
        
        # Extract a sample of the therapeutic instructions
        if 'step-instructions' in content:
            print("\n📝 Sample Instructions Found in HTML:")
            # Simple extraction to show instructions are present
            lines = content.split('\n')
            instruction_lines = []
            in_instructions = False
            
            for line in lines:
                if 'step-instructions' in line:
                    in_instructions = True
                elif '</ul>' in line and in_instructions:
                    in_instructions = False
                elif in_instructions and '<li>' in line:
                    # Extract instruction text
                    text = line.strip()
                    if '🎯' in text or '💆‍♀️' in text or '🔄' in text:
                        instruction_lines.append(text)
                        if len(instruction_lines) >= 3:  # Show first 3 found
                            break
            
            for line in instruction_lines:
                print(f"    {line}")
        
        # Save sample for inspection
        with open('/workspaces/codespaces-blank/therapeutic_stretching_test.html', 'w') as f:
            f.write(content)
        
        print(f"\n📄 Full HTML saved to therapeutic_stretching_test.html")
        print("\n🎉 Therapeutic stretching should now have detailed, specific instructions!")
        
    else:
        print(f"❌ Failed with status {response.status_code}")
        print(response.text[:500] if response.text else "No response content")

if __name__ == "__main__":
    test_therapeutic_stretching()
