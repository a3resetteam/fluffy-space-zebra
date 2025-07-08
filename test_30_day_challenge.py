#!/usr/bin/env python3
"""
Test script to verify all Strategic Mastery modules are accessible
"""

import requests
import sys

BASE_URL = "http://localhost:5001"

# List of all Strategic Mastery module routes
MODULES = [
    "/alpha-elite/strategic-mastery",
    "/alpha-elite/strategic-mastery/strategic-observation", 
    "/alpha-elite/strategic-mastery/communication-mastery",
    "/alpha-elite/strategic-mastery/presence-authority",
    "/alpha-elite/strategic-mastery/strategic-thinking",
    "/alpha-elite/strategic-mastery/ai-framework", 
    "/alpha-elite/strategic-mastery/schedule-performance",
    "/alpha-elite/strategic-mastery/30-day-challenge"  # New module
]

def test_modules():
    """Test that all modules are accessible"""
    print("🧪 Testing Strategic Mastery Modules...")
    print("="*50)
    
    session = requests.Session()
    
    for module_path in MODULES:
        url = BASE_URL + module_path
        try:
            response = session.get(url, timeout=10)
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            module_name = module_path.split("/")[-1].replace("-", " ").title()
            print(f"{status:8} | {module_name:25} | {url}")
            
            # Check if the new 30-day-challenge module contains expected content
            if "30-day-challenge" in module_path and response.status_code == 200:
                content = response.text
                if "30 Day Alpha Elite Challenge" in content and "🏆" in content:
                    print(f"         | ✅ Contains expected content")
                else:
                    print(f"         | ⚠️  Missing expected content")
                    
        except Exception as e:
            print(f"❌ ERROR | {module_path:25} | {str(e)}")
    
    print("="*50)
    print("✅ Module testing complete!")

if __name__ == "__main__":
    test_modules()
