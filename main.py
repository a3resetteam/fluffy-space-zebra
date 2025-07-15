#!/usr/bin/env python3
"""
Railway production entry point for MYA3Reset: The Oracle
"""
import os
from app_fixed import app, init_db, create_admin_user

if __name__ == '__main__':
    # Initialize database and admin user
    init_db()
    create_admin_user()
    
    # Get port from Railway environment
    port = int(os.environ.get('PORT', 8080))
    
    print(f"🚀 Oracle Platform starting on port {port}")
    print("🔐 Admin login: /admin/login (username: admin, password: admin123)")
    
    # Run with production settings
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=False  # Important: Set to False for production
    )