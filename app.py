import subprocess
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clicker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------- MODELS -------------------- #
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    total_clicks = db.Column(db.Integer, default=0)
    total_time = db.Column(db.Float, default=0.0)
    multiplier = db.Column(db.Integer, default=1)
    multiplier_expires = db.Column(db.DateTime, nullable=True)

# -------------------- ROUTES -------------------- #

@app.route('/')
def index():
    return redirect(url_for('clicker')) if 'user_id' in session else redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken! Try another.", "danger")
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success") 
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            session['login_time'] = time.time()  # Track session start
            flash("Login successful!", "success")
            return redirect(url_for('clicker'))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/clicker')
def clicker():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    login_time = datetime.fromtimestamp(session.get('login_time', time.time()))
    current_time = datetime.utcnow()
    session_time = (current_time - login_time).total_seconds()

    return render_template('clicker.html', clicks=user.total_clicks, session_time=session_time)

@app.route('/click', methods=['POST'])
def click():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user = User.query.get(session['user_id'])
    
    # Call the Java program to get the current multiplier
    result = subprocess.run(['java', 'MultiplierManager'], capture_output=True, text=True)

    multiplier = int(result.stdout.strip())  # Read multiplier from Java program output

    if multiplier > 1:
        added_clicks = int(1 * multiplier)
        user.total_clicks += added_clicks
        user.multiplier = multiplier
        user.multiplier_expires = datetime.utcnow() + timedelta(seconds=(30 if multiplier == 2 else 20))

    db.session.commit()

    return jsonify({'clicks': user.total_clicks, 'multiplier': multiplier})

if __name__ == '__main__':
    app.run(debug=True)
