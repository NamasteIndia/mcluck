import os
import bcrypt
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)

# Secret key for session signing
app.secret_key = os.environ.get("SECRET_KEY", "tata_steel_safety_2026_portal")

# MongoDB Configuration
# Ensure you have set MONGO_URI in Koyeb Environment Variables
mongo_uri = os.environ.get("MONGO_URI")
if not mongo_uri:
    print("CRITICAL: MONGO_URI environment variable is missing!")

app.config["MONGO_URI"] = mongo_uri
mongo = PyMongo(app)

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
        if mongo.db is None:
            return "Database connection error. Please check MONGO_URI.", 500
            
        users = mongo.db.users
        user = users.find_one({'username': request.form['username']})
        
        if user and bcrypt.checkpw(request.form['password'].encode('utf-8'), user['password']):
            session['username'] = user['username']
            return redirect(url_for('index'))
        
        return "Invalid User ID or Password. <a href='/login'>Try again</a>", 401
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Employee Registration"""
    if request.method == 'POST':
        if mongo.db is None:
            return "Database connection error.", 500
            
        users = mongo.db.users
        # Check if ID already registered
        if users.find_one({'username': request.form['username']}):
            return "User ID already exists! <a href='/register'>Try another</a>", 400
            
        # Hash password and save
        hashed_pw = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        users.insert_one({
            'username': request.form['username'], 
            'password': hashed_pw, 
            'last_score': 0
        })
        return redirect(url_for('login'))
    
    # This ensures the page loads when the user visits the URL
    return render_template('register.html')

@app.route('/submit-score', methods=['POST'])
def submit_score():
    """Save Quiz Results to MongoDB"""
    if 'username' in session:
        data = request.json
        score = data.get('score', 0)
        
        mongo.db.users.update_one(
            {'username': session['username']},
            {'$set': {'last_score': score}}
        )
        return jsonify({"status": "success", "score": score})
    return jsonify({"status": "error", "message": "Unauthorized"}), 401

@app.route('/profile')
def profile():
    """User Result Dashboard"""
    if 'username' in session:
        user_data = mongo.db.users.find_one({'username': session['username']})
        
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
