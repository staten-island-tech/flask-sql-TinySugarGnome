from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import time
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clicker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------- MODELS -------------------- #
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)  # Simple password storage
    total_clicks = db.Column(db.Integer, default=0)
    total_time = db.Column(db.Float, default=0.0)
    multiplier = db.Column(db.Integer, default=1)
    multiplier_expires = db.Column(db.DateTime, nullable=True)
# -------------------- ROUTES -------------------- #
@app.route('/')
def index():
    return redirect(url_for('clicker')) if 'user_id' in session else redirect(url_for('login'))


#THE PASSWORD SHOULD BE EXTREMELY SIMPLE. ONLY UYSERNAME AND LOGIN. THATS IT. SIMPLE. THIS IS A TEST PROECT
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken! Try another.", "danger")
            return redirect(url_for('register'))

        # Store the username and password as plain text
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login(): #the form
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists in the database
        user = User.query.filter_by(username=username).first() #filters through usernames

        if user and user.password == password:  # Simple password check 
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
    if 'user_id' not in session:
        return redirect(url_for('login'))
@app.route('/clicker')
def clicker():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('clicker.html', clicks=user.total_clicks)

@app.route('/click', methods=['POST'])
def click():
    pass

@app.route('/leaderboard')
def leaderboard():
    # show top 5 users
    pass

@app.route('/admin')
def admin():
    # list all users and stats
    pass

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)