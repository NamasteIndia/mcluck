import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)
app.secret_key = "super_secret_safety_key"

# 1. Get the URI from Environment
mongo_uri = os.environ.get("MONGO_URI")

# 2. Safety check: If URI is missing, print a clear error in the logs
if not mongo_uri:
    print("CRITICAL ERROR: MONGO_URI environment variable is not set!")

app.config["MONGO_URI"] = mongo_uri
# 3. Initialize PyMongo
mongo = PyMongo(app)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check if db connection exists before using it
        if mongo.db is None:
            return "Database connection failed. Check your MONGO_URI and Atlas IP Whitelist.", 500
            
        users = mongo.db.users

@app.route('/profile')
def profile():
    if 'username' in session:
        users = mongo.db.users
        user_data = users.find_one({'username': session['username']})
        
        # Calculate status
        last_score = user_data.get('last_score', 0)
        status = "PASSED" if last_score >= 10 else "FAILED"
        status_color = "text-green-400" if status == "PASSED" else "text-rose-500"
        
        return render_template('profile.html', 
                               user=user_data, 
                               status=status, 
                               status_color=status_color)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        user = users.find_one({'username': request.form['username']})
        if user and bcrypt.checkpw(request.form['password'].encode('utf-8'), user['password']):
            session['username'] = user['username']
            return redirect(url_for('index'))
        return "Invalid username/password"
    return render_template('login.html')

@app.route('/submit-score', methods=['POST'])
def submit_score():
    if 'username' in session:
        data = request.json
        mongo.db.users.update_one(
            {'username': session['username']},
            {'$set': {'last_score': data['score']}}
        )
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 401

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
