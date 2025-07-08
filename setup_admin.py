#!/usr/bin/env python3
"""
Setup script to configure CEO admin access for MYA3Reset Oracle
"""

import os
import sys
from getpass import getpass

def setup_admin():
    print("🔮 Oracle Admin Setup")
    print("=" * 50)
    
    # Get CEO credentials
    print("\n📧 CEO Email Setup:")
    ceo_email = input("Enter your CEO email: ").strip()
    
    print("\n🔐 CEO Password Setup:")
    ceo_password = getpass("Enter a secure admin password: ").strip()
    ceo_password_confirm = getpass("Confirm password: ").strip()
    
    if ceo_password != ceo_password_confirm:
        print("❌ Passwords don't match!")
        return False
    
    if len(ceo_password) < 8:
        print("❌ Password must be at least 8 characters!")
        return False
    
    # Update the app.py file with the credentials
    try:
        with open('/workspaces/codespaces-blank/app.py', 'r') as f:
            content = f.read()
        
        # Replace the placeholder credentials
        content = content.replace(
            'CEO_EMAIL = "ceo@mya3reset.com"  # Change this to your email',
            f'CEO_EMAIL = "{ceo_email}"'
        )
        content = content.replace(
            'CEO_PASSWORD = "Oracle2025!"     # Change this to your secure password',
            f'CEO_PASSWORD = "{ceo_password}"'
        )
        
        with open('/workspaces/codespaces-blank/app.py', 'w') as f:
            f.write(content)
        
        print(f"\n✅ Admin credentials configured!")
        print(f"📧 CEO Email: {ceo_email}")
        print(f"🔑 Password: {'*' * len(ceo_password)}")
        print(f"\n🔗 Access your admin panel at:")
        print(f"   https://fluffy-space-zebra-4jr6vqjp5694cqjq-5000.app.github.dev/admin")
        print(f"\n🛡️  Only you can access this panel with these credentials.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating credentials: {e}")
        return False

if __name__ == "__main__":
    success = setup_admin()
    if success:
        print(f"\n🎉 Setup complete! Your Oracle admin panel is ready.")
    else:
        print(f"\n❌ Setup failed. Please try again.")
        sys.exit(1)
