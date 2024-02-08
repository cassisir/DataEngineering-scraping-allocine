from flask import Flask, render_template, request
from pymongo import MongoClient
from search_and_filter import apply_filters
from bson import ObjectId
from graphs import movies_per_genre_graph, mean_ratings_per_genre_graph, mean_ratings_date_graph

app = Flask(__name__)

client = MongoClient('mongo', 27017)
db = client.allocine
collection = db.movie_collection

@app.route('/')
def index():
    genre_request = request.args.get('genre')
    sort_by_request = request.args.get('sort_by', 'date')
    sort_order_request = request.args.get('sort_order', 'descending')
    search_query = request.args.get('search_query', '').strip()
    exclude_not_rated = request.args.get('exclude_not_rated') == 'on'

    movies = apply_filters(collection, genre_request, sort_by_request, sort_order_request, exclude_not_rated, search_query)

    all_genres = list(collection.distinct('genre'))
    return render_template('index.html', movies=movies, all_genres=all_genres, selected_genre=genre_request, selected_sort_by=sort_by_request, selected_order=sort_order_request, exclude_not_rated=exclude_not_rated)


@app.route('/movie/<movie_id>')
def movie(movie_id):
    movie = collection.find_one({'_id': movie_id})
    return render_template('movie.html', movie=movie)

@app.route('/graphs')
def graphs():
    movies_per_genre_fig = movies_per_genre_graph(collection)
    mean_ratings_per_genre = mean_ratings_per_genre_graph(collection)
    mean_ratings_date = mean_ratings_date_graph(collection)

    return render_template('graphs.html',
                           movies_per_genre_fig=movies_per_genre_fig,
                           mean_ratings_per_genre_fig=mean_ratings_per_genre,
                           mean_ratings_date_fig=mean_ratings_date)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
