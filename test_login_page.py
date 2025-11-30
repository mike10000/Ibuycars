"""
Simple test route to view the login page
Add this to app.py or run this file separately
"""
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/login')
def login():
    """Display the login page"""
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
