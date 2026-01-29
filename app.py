import os
import json
import bcrypt
import base64
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from dotenv import load_dotenv
import fcntl
import time

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Secret key for session signing
app.secret_key = os.environ.get("SECRET_KEY", "tata_steel_safety_2026_portal")

# Local Storage Configuration
DATA_FILE = 'users_data.json'

def load_users():
    """Load users from local JSON file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Shared lock for reading
                try:
                    return json.load(f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Unlock
        return {}
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading users: {e}")
        return {}

def save_users(users):
    """Save users to local JSON file with file locking"""
    try:
        # Write to temporary file first, then rename for atomic operation
        temp_file = DATA_FILE + '.tmp'
        with open(temp_file, 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock for writing
            try:
                json.dump(users, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Unlock
        os.replace(temp_file, DATA_FILE)  # Atomic rename
        return True
    except (IOError, OSError) as e:
        print(f"Error saving users: {e}")
        return False

def get_user(username):
    """Get a user by username"""
    users = load_users()
    return users.get(username)

def update_user(username, data):
    """Update user data"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            users = load_users()
            if username in users:
                users[username].update(data)
                if save_users(users):
                    return True
            return False
        except Exception as e:
            print(f"Error updating user (attempt {attempt + 1}): {e}")
            time.sleep(0.1)  # Brief delay before retry
    return False

def create_user(username, password):
    """Create a new user"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            users = load_users()
            if username in users:
                return False
            users[username] = {
                'username': username,
                'password': password,
                'last_score': 0
            }
            if save_users(users):
                return True
            return False
        except Exception as e:
            print(f"Error creating user (attempt {attempt + 1}): {e}")
            time.sleep(0.1)  # Brief delay before retry
    return False

# --- ROUTES ---

@app.route('/')
def index():
    """Main Quiz Page - Requires Login"""
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Student Login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return render_template('login.html', error="Please provide both username and password."), 200
        
        user = get_user(username)
        
        if user and bcrypt.checkpw(password.encode('utf-8'), base64.b64decode(user['password'])):
            session['username'] = user['username']
            return redirect(url_for('index'))
        
        return render_template('login.html', error="Invalid User ID or Password. Please try again."), 200
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Student Registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validate input
        if not username or not password:
            return render_template('register.html', error="Username and password are required."), 200
        
        if len(username) < 3 or len(username) > 50:
            return render_template('register.html', error="Username must be between 3 and 50 characters."), 200
        
        if len(password) < 6:
            return render_template('register.html', error="Password must be at least 6 characters long."), 200
        
        # Check if ID already registered
        if get_user(username):
            return render_template('register.html', error="User ID already exists! Please try another ID."), 200
            
        # Hash password and save (using base64 encoding for storage)
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_pw_str = base64.b64encode(hashed_pw).decode('utf-8')
        
        if create_user(username, hashed_pw_str):
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
        
        if update_user(session['username'], {'last_score': score}):
            return jsonify({"status": "success", "score": score})
        else:
            return jsonify({"status": "error", "message": "Failed to save score"}), 500
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
