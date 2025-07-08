#!/usr/bin/env python3
print("Testing Python...")
from flask import Flask
print("Flask imported successfully")
app = Flask(__name__)

@app.route('/')
def hello():
    return "Oracle is working!"

if __name__ == '__main__':
    print("Starting test server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
