Skip to main content
Google Classroom
Classroom
Comp Sci/Engineering T1
SKS21T_20 (Period 2) 2024 2
Home
Calendar
Enrolled
To-do
N
NGLS Geometry Regents Review Tutoring
A
AI CLUB
F
FTC Robotics Interest 24-25
L
Letter to Myself: 9th Grade Project
P
Period 8: Geometry T2
MGS22H_85 (Period 8) 2024 2
C
Comp Sci/Engineering T1
SKS21T_20 (Period 2) 2024 2
C
Chemistry Lab T2
SCS22QL_92 (Period 9) 2024 2
C
Chemistry P1 - Term 2
SCS22H_19 (Period 1) 2024 2
H
Health Education
PHS11_38 (Period 3) 2024 2
A
AP World History T2
HGS42X_40 (Period 4) 2024 2
I
Intro Tech Careers T2
RZS22TF_53 (Period 5) 2024 2
R
Russian T2
FRS62H_61 (Period 6) 2024 2
E
English T2 Writing
EES82HW_75 (Period 7) 2024 2
A
Arts & Crafts Club
F
Freshmen SERP
January 2025
S
SITHS Library Google Classroom 2
N
NHS Cohort Class of 2028
S
Soap Smiles
C
Career Development Center 2024-2025
Room 229
P
Pd 4 - Russian T1
FRS61H_46 (Period 4) 2024 1
C
Class of 2028 - College Advisement
GAS11QC_9 (Period 13) 2023 2
P
Period 3: Geometry T1
MGS21H_35 (Period 3) 2024 1
Archived classes
Settings
Flask with SQL Project
Flask with SQL Project
Michael Whalen
•
Yesterday
Learning Progress
•
20 points
PD2: https://classroom.github.com/a/AcF3h5AO

PD3: https://classroom.github.com/a/PdxOrLro

Flask Docs https://flask.palletsprojects.com/en/stable/

sql.md
Text

Flask SQL Project.pdf
PDF
Class comments
Your work
Assigned
Private comments
# **🎬 Storing Movie Ticket Bookings in a Database **  

Hey there! 👋 So far, we've built a **Flask website** that lets users book movie tickets. 🎟️  

Right now, after booking a ticket, we **only show a message** like:  
```
Booking confirmed for Alice, 2 seat(s) for Avengers: Endgame!
```
But what if we want to **save** this booking so we can check it later? 🤔  

The answer: **Databases!**  

---

## **📌 What is a Database?**
A **database** is like a **digital notebook** where we store information.  
- Every time a user **books a ticket**, we write it in this notebook.  
- Later, we can **read the notebook** to see all the bookings.  

We will use **SQLite**, a simple database that **comes with Python**.  

---

# **🛠 Step 1: Install Flask-SQLAlchemy (Database Tool for Flask)**  

Before using a database, we need to install **Flask-SQLAlchemy**.  

💻 **In your terminal, run this command:**  
```bash
pip install Flask-SQLAlchemy
```
This **installs a library** that helps Flask **talk to our database**. 📚  

---

# **📌 Step 2: Set Up the Database in Flask**
### **Modify `app.py` to Use a Database**
Now, we need to tell Flask:
- **Where the database is stored**  
- **What kind of data we will store**  

Open `app.py` and modify it like this:

```python
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
```

---

# **🔎 Step 2.1: Understanding the Code**
### **📌 What is `SQLAlchemy`?**
SQLAlchemy is a tool that helps Flask **talk to the database** easily.  
- Instead of writing complicated SQL commands, we use **Python classes** to define **tables**.  

---

### **📌 What is `Booking(db.Model)`?**
This **creates a "Bookings" table** in the database to store information.  

| **Column Name**  | **Type**  | **Description** |
|-----------------|----------|----------------|
| `id`           | Integer  | Unique ID for each booking |
| `name`         | String   | Name of the person booking |
| `movie_title`  | String   | The movie name |
| `seats`        | Integer  | Number of seats booked |

📌 **Each row in this table represents one booking.**  

---

# **📌 Step 3: Save Bookings to the Database**
Now, update the **booking function** in `app.py` to save user bookings.

```python
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
```

---

### **🔎 Step 3.1: How Does This Work?**
1️⃣ **Find the correct movie** based on `movie_id`.  
2️⃣ **If the movie doesn’t exist**, show an error message.  
3️⃣ **If the form is submitted (`POST` request)**:  
   - Get the user's **name** and **number of seats** from the form.  
   - Create a **new booking** in the database.  
   - **Save the booking** using `db.session.add()` and `db.session.commit()`.  
   - Redirect to a **confirmation page**.  

---

# **📌 Step 4: Create a Confirmation Page**
Now, let's **create a new page** that shows a booking confirmation.

### **Modify `app.py` to Add This Route**
```python
@app.route('/confirmation')
def confirmation():
    name = request.args.get('name')
    movie_title = request.args.get('movie_title')
    seats = request.args.get('seats')
    return render_template('confirmation.html', name=name, movie_title=movie_title, seats=seats)
```

---

### **Create `templates/confirmation.html`**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Booking Confirmed</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
</head>
<body>
    <h1>✅ Booking Confirmed!</h1>
    <p>Thank you, <strong>{{ name }}</strong>! Your booking for <strong>{{ movie_title }}</strong> ({{ seats }} seat(s)) has been saved.</p>
    <a href="{{ url_for('home') }}">⬅️ Back to Movies</a>
</body>
</html>
```

---

# **📌 Step 5: Create an Admin Page to View Bookings**
Now, let's create a **page for admins** to see all the bookings.

### **Modify `app.py` to Add This Route**
```python
@app.route('/admin/bookings')
def view_bookings():
    bookings = Booking.query.all()
    return render_template('bookings.html', bookings=bookings)
```

### **Create `templates/bookings.html`**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Bookings</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
</head>
<body>
    <h1>📜 All Bookings</h1>
    <table border="1">
        <tr>
            <th>Name</th>
            <th>Movie</th>
            <th>Seats</th>
        </tr>
        {% for booking in bookings %}
        <tr>
            <td>{{ booking.name }}</td>
            <td>{{ booking.movie_title }}</td>
            <td>{{ booking.seats }}</td>
        </tr>
        {% endfor %}
    </table>
    <br>
    <a href="{{ url_for('home') }}">⬅️ Back to Movies</a>
</body>
</html>
```

---

# **🚀 Step 6: Run Your Flask App!**
```bash
python app.py
```

- **Book a ticket** → It **saves the booking** 🎟️  
- **Visit** `http://127.0.0.1:5000/admin/bookings` → **See all bookings**! 🎉  

---

## **✅ Summary**
✔ **Added SQLite database to store bookings**  
✔ **Created a table for bookings using SQLAlchemy**  
✔ **Saved user data in the database**  
✔ **Created an admin page to view bookings**  

Want to level up? Try **adding user logins** next! 🚀🎟️
sql.md
Displaying sql.md.