from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask import jsonify
import time
import random
import subprocess
import threading

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

current_multiplier = 1
multiplier_expires = 0  # epoch ms (in milliseconds)

def run_java_multiplier():
    global current_multiplier, multiplier_expires
    process = subprocess.Popen(['java', 'MultiplierManager'], stdout=subprocess.PIPE, text=True)
    while True:
        line = process.stdout.readline()
        if line:
            try:
                val = int(line.strip())
                if val in [2, 10]:
                    current_multiplier = val
                    expires_line = process.stdout.readline()
                    multiplier_expires = int(expires_line.strip())
            except ValueError:
                continue

def get_active_multiplier():
    if time.time() * 1000 > multiplier_expires:
        return 1
    return current_multiplier

# Start background Java multiplier thread
threading.Thread(target=run_java_multiplier, daemon=True).start()
# -------------------- ROUTES -------------------- #
@app.route('/')
def index():
    return redirect(url_for('clicker')) if 'user_id' in session else redirect(url_for('login'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken! Try another.", "danger") #wth does danger mean
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
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/update_time', methods=['POST'])
def update_time():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    session_time = data.get('session_time')

    if session_time is None:
        return jsonify({'error': 'Invalid data'}), 400

    user = User.query.get(session['user_id'])
    user.total_time += session_time
    db.session.commit()

    return jsonify({'status': 'success'})

@app.route('/clicker')
def clicker():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    login_time = datetime.fromtimestamp(session.get('login_time', time.time()))
    
    # Time online in current session
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
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user = User.query.get(session['user_id'])

    # Check if the user's multiplier is still active
    if user.multiplier_expires and user.multiplier_expires < datetime.utcnow():
        # If expired, reset multiplier to 1 and expiration time
        user.multiplier = 1
        user.multiplier_expires = None

    # Use the user's own multiplier to calculate the clicks
    added_clicks = int(1 * user.multiplier)
    user.total_clicks += added_clicks

    db.session.commit()

    return jsonify({
        'clicks': user.total_clicks  # Return the updated click count for the user
    })


@app.route('/multiplier-check')
def multiplier_check():
    multiplier = get_active_multiplier()
    return jsonify({'multiplier': multiplier})

@app.route('/leaderboard')
def leaderboard():
    top_users = User.query.order_by(User.total_clicks.desc()).limit(10).all() #well... self explanitory
    top_time_users = User.query.order_by(User.total_time.desc()).limit(10).all()

    return render_template('leaderboard.html', top_users=top_users, top_time_users=top_time_users)

@app.route('/admin')
def admin():
    # Fetch all users
    users = User.query.all()

    # Render the admin page with all users' data
    return render_template('admin.html', users=users)


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