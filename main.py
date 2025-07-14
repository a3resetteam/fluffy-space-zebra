#!/usr/bin/env python3
"""
Main entry point for Railway deployment
"""

from app_fixed import app, init_db
import os

if __name__ == '__main__':
    init_db()
    
    # Check if running on Railway (production)
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        print("🚀 Oracle Platform starting on Railway with gunicorn...")
        # Railway will use gunicorn via Procfile or startCommand
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("🔧 Running in development mode...")
        app.run(host='0.0.0.0', port=5000, debug=True)
