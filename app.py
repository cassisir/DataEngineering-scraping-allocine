from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.allocine
collection = db.movie_collection

@app.route('/')
def index():
    # Filtre de genre
    selected_genre = get_genre_filter(request)
    # Filtre de tri
    sort_by = request.args.get('sort_by', 'press_rating')
    sort_field = 'ratings.press' if sort_by == 'press_rating' else 'ratings.spectators'
    # Ordre du tri
    sort_order = request.args.get('sort_order', 'descending')
    order = 1 if sort_order == 'ascending' else -1
    # Retire les films non notés si checkbox cochée
    exclude_not_rated = request.args.get('exclude_not_rated') == 'on'
    query = selected_genre
    if exclude_not_rated:
        query[sort_field] = {'$ne': 'not rated'} # Ajoute la condition pour ne conserver que les films notés

    # Sélection des films
    movies = list(collection.find(selected_genre).sort(sort_field, order))

    all_genres = list(collection.distinct('genre'))
    return render_template('index.html', movies=movies, all_genres=all_genres, selected_genre=selected_genre, selected_sort_by=sort_by, selected_order=sort_order, exclude_not_rated=exclude_not_rated)


@app.route('/movie/<title>')
def movie(title):
    movie = collection.find_one({'title': title})
    return render_template('movie.html', movie=movie)


@app.route('/graphs')
def graphs():
    sample_data = {'genres': ['Action', 'Comedy', 'Drama'],
                   'count': [15, 20, 25]}

    return render_template('graphs.html', data=sample_data)


def get_genre_filter(request):
    selected_genre = request.args.get('genre')
    genre_filter = {'genre': selected_genre} if selected_genre else {}
    return genre_filter

if __name__ == '__main__':
    app.run(debug=True)