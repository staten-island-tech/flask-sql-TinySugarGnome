from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 📌 Tell Flask where the database file will be stored
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 📌 Create the database object
db = SQLAlchemy(app)

# 🎬 Sample movie data
movies = [
    {"id": 1, "title": "Avengers: Endgame", "price": 12},
    {"id": 2, "title": "Spider-Man: No Way Home", "price": 10},
    {"id": 3, "title": "Inception", "price": 8}
]

# 📌 Define the Booking Model (Table)
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each booking
    name = db.Column(db.String(100), nullable=False)  # User's name
    movie_title = db.Column(db.String(100), nullable=False)  # Movie booked
    seats = db.Column(db.Integer, nullable=False)  # Number of seats booked

# 📌 Create the database table
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html', movies=movies)
@app.route('/book/<int:movie_id>', methods=['GET', 'POST'])
def book(movie_id):
    # Find the movie using movie_id
    movie = next((m for m in movies if m["id"] == movie_id), None)

    if not movie:
        return "Movie not found", 404

    if request.method == 'POST':
        name = request.form['name']
        seats = int(request.form['seats'])

        # 📌 Create a new Booking and save it to the database
        new_booking = Booking(name=name, movie_title=movie["title"], seats=seats)
        db.session.add(new_booking)
        db.session.commit()

        return redirect(url_for('confirmation', name=name, movie_title=movie["title"], seats=seats))

    return render_template('book.html', movie=movie)
@app.route('/confirmation')
def confirmation():
    name = request.args.get('name')
    movie_title = request.args.get('movie_title')
    seats = request.args.get('seats')
    return render_template('confirmation.html', name=name, movie_title=movie_title, seats=seats)
@app.route('/admin/bookings')
def view_bookings():
    bookings = Booking.query.all()
    return render_template('bookings.html', bookings=bookings)
if __name__ == '__main__':
    app.run(debug=True)