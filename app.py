import os
import json
import bcrypt
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Secret key for session signing
app.secret_key = os.environ.get("SECRET_KEY", "tata_steel_safety_2026_portal")

# Local Storage Configuration
DATA_FILE = 'users_data.json'

def load_users():
    """Load users from local JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to local JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def get_user(username):
    """Get a user by username"""
    users = load_users()
    return users.get(username)

def update_user(username, data):
    """Update user data"""
    users = load_users()
    if username in users:
        users[username].update(data)
        save_users(users)
        return True
    return False

def create_user(username, password):
    """Create a new user"""
    users = load_users()
    if username in users:
        return False
    users[username] = {
        'username': username,
        'password': password,
        'last_score': 0
    }
    save_users(users)
    return True

# --- ROUTES ---

@app.route('/')
def index():
    """Main Quiz Page - Requires Login"""
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Employee Login"""
    if request.method == 'POST':
        user = get_user(request.form['username'])
        
        if user and bcrypt.checkpw(request.form['password'].encode('utf-8'), user['password'].encode('latin-1')):
            session['username'] = user['username']
            return redirect(url_for('index'))
        
        return render_template('login.html', error="Invalid User ID or Password. Please try again."), 200
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Employee Registration"""
    if request.method == 'POST':
        username = request.form['username']
        # Check if ID already registered
        if get_user(username):
            return render_template('register.html', error="User ID already exists! Please try another ID."), 200
            
        # Hash password and save
        hashed_pw = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        if create_user(username, hashed_pw.decode('latin-1')):
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error="Registration failed. Please try again."), 200
    
    # This ensures the page loads when the user visits the URL
    return render_template('register.html')

@app.route('/submit-score', methods=['POST'])
def submit_score():
    """Save Quiz Results to Local Storage"""
    if 'username' in session:
        data = request.json
        score = data.get('score', 0)
        
        update_user(session['username'], {'last_score': score})
        return jsonify({"status": "success", "score": score})
    return jsonify({"status": "error", "message": "Unauthorized"}), 401

@app.route('/profile')
def profile():
    """User Result Dashboard"""
    if 'username' in session:
        user_data = get_user(session['username'])
        
        if not user_data:
            return redirect(url_for('login'))
        
        # Grading Logic: Total Marks = 50, Pass = 10
        last_score = user_data.get('last_score', 0)
        status = "PASSED" if last_score >= 10 else "FAILED"
        status_color = "text-green-400" if status == "PASSED" else "text-rose-500"
        
        return render_template('profile.html', 
                               user=user_data, 
                               status=status, 
                               status_color=status_color)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """End Session"""
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    # Koyeb provides the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
