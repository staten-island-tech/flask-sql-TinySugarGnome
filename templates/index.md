<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movie Ticket Booking</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
</head>
<body>
    <h1>🎬 Movie Ticket Booking</h1>

    <div class="movies">
        {% for movie in movies %}
            <div class="movie">
                <h2>{{ movie.title }}</h2>
                <p>Price: ${{ movie.price }}</p>
                <a href="{{ url_for('book', movie_id=movie.id) }}"><button>Book Now</button></a>
            </div>
        {% endfor %}
    </div>

</body>
</html>