from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import time
import random
import threading
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'your_database.db')

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
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

# -------------------- HELPERS -------------------- #
def get_current_user():
    """Helper to get user from session or redirect if not found."""
    if 'user_id' not in session:
        return None
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash("User not found, please log in again.", "warning")
        return None
    return user

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
            session['login_time'] = time.time()
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

@app.route('/update_time', methods=['POST'])
def update_time():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    session_time = data.get('session_time')

    if session_time is None:
        return jsonify({'error': 'Invalid data'}), 400

    user.total_time += session_time
    db.session.commit()

    return jsonify({'status': 'success'})

@app.route('/clicker')
def clicker():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    login_time = datetime.fromtimestamp(session.get('login_time', time.time()))
    current_time = datetime.utcnow()
    session_time = (current_time - login_time).total_seconds()

    return render_template(
        'clicker.html',
        clicks=user.total_clicks,
        multiplier=user.multiplier,
        multiplier_expires=user.multiplier_expires,
        session_time=session_time
    )

@app.route('/click', methods=['POST'])
def click():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    # Reset multiplier if expired
    if user.multiplier_expires and user.multiplier_expires < datetime.utcnow():
        user.multiplier = 1
        user.multiplier_expires = None

    added_clicks = 1 * user.multiplier
    user.total_clicks += added_clicks
    db.session.commit()

    return jsonify({
        'clicks': user.total_clicks,
        'multiplier': user.multiplier,
        'expires': user.multiplier_expires.isoformat() if user.multiplier_expires else None
    })

@app.route('/leaderboard')
def leaderboard():
    top_users = User.query.order_by(User.total_clicks.desc()).limit(10).all()
    top_time_users = User.query.order_by(User.total_time.desc()).limit(10).all()

    return render_template('leaderboard.html', top_users=top_users, top_time_users=top_time_users)

@app.route('/admin')
def admin():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

# -------------------- BACKGROUND MULTIPLIER LOGIC -------------------- #
def random_multiplier_loop():
    while True:
        with app.app_context():
            now = datetime.utcnow()
            active_cutoff = now - timedelta(seconds=30)

            # Active users (update multiplier)
            active_users = User.query.filter(User.last_seen >= active_cutoff).all()

            # Reset multipliers for inactive users
            inactive_users = User.query.filter(User.last_seen < active_cutoff, User.multiplier != 1).all()
            for user in inactive_users:
                user.multiplier = 1
                user.multiplier_expires = None
                print(f"[{user.username}] Multiplier reset due to inactivity.")

            for user in active_users:
                # Reset multiplier if expired
                if user.multiplier_expires and user.multiplier_expires < now:
                    user.multiplier = 1
                    user.multiplier_expires = None

                roll = random.randint(1, 1000)
                new_multiplier = None
                duration = 0

                if roll == 1:
                    new_multiplier = 100
                    duration = 5
                elif roll <= 3:
                    new_multiplier = 50
                    duration = 5
                elif roll <= 7:
                    new_multiplier = 30
                    duration = 8
                elif roll <= 27:
                    new_multiplier = 10
                    duration = 7
                elif roll <= 127:
                    new_multiplier = 2
                    duration = 5

                if new_multiplier:
                    if user.multiplier < new_multiplier:
                        user.multiplier = new_multiplier
                        user.multiplier_expires = now + timedelta(seconds=duration)
                        print(f"[{user.username}] New multiplier: {new_multiplier} for {duration}s")
                    elif user.multiplier == new_multiplier and user.multiplier_expires:
                        user.multiplier_expires += timedelta(seconds=duration)
                        print(f"[{user.username}] Extended multiplier {new_multiplier} by {duration}s")

            db.session.commit()

        time.sleep(1)

@app.before_request
def update_last_seen():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            user.last_seen = datetime.utcnow()
            db.session.commit()

# -------------------- START BACKGROUND THREAD -------------------- #
def start_background_task():
    thread = threading.Thread(target=random_multiplier_loop)
    thread.daemon = True
    thread.start()

with app.app_context():
    db.create_all()

start_background_task()

if __name__ == '__main__':
    app.run(debug=True)
