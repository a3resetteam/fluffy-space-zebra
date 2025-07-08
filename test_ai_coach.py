#!/usr/bin/env python3
"""Test script to check AI coach functionality"""

import sys
import os
import subprocess

def test_html_syntax():
    """Test if the HTML file has valid syntax"""
    html_file = "/workspaces/codespaces-blank/templates/ai-coach.html"
    
    try:
        with open(html_file, 'r') as f:
            content = f.read()
        
        # Check for basic HTML structure
        if not content.startswith('{% extends "base.html" %}'):
            print("❌ HTML file doesn't start with proper Flask template syntax")
            return False
            
        # Check for unmatched braces or brackets
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_braces != close_braces:
            print(f"❌ Unmatched braces: {open_braces} open, {close_braces} close")
            return False
            
        # Check for script tags
        if '<script>' not in content or '</script>' not in content:
            print("❌ Missing script tags")
            return False
            
        print("✅ Basic HTML syntax looks good")
        return True
        
    except Exception as e:
        print(f"❌ Error reading HTML file: {e}")
        return False

def test_javascript_functions():
    """Test if key JavaScript functions are present"""
    html_file = "/workspaces/codespaces-blank/templates/ai-coach.html"
    
    required_functions = [
        'selectCoach',
        'sendMessage',
        'addMessageToChat',
        'generateCoachResponse',
        'viewChatHistory',
        'changeCoach',
        'useQuickPrompt',
        'handleKeyPress',
        'showToast'
    ]
    
    try:
        with open(html_file, 'r') as f:
            content = f.read()
        
        missing_functions = []
        for func in required_functions:
            if f'function {func}(' not in content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"❌ Missing functions: {', '.join(missing_functions)}")
            return False
        else:
            print("✅ All required JavaScript functions are present")
            return True
            
    except Exception as e:
        print(f"❌ Error checking JavaScript functions: {e}")
        return False

def main():
    print("🔍 Testing AI Coach implementation...")
    print("-" * 50)
    
    html_ok = test_html_syntax()
    js_ok = test_javascript_functions()
    
    if html_ok and js_ok:
        print("\n✅ AI Coach implementation looks good!")
        print("The issue might be in the Flask app setup or routes.")
        return True
    else:
        print("\n❌ Found issues in AI Coach implementation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
