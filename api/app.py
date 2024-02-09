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
    """
    Page principale affichant tous les films dans cartes avec une sélection de filtre et un champ de recherche.
    """
    # Récupère les filtres sélectionnés
    genre_request = request.args.get('genre')                               # Dropdown menu : Filtre genre
    sort_by_request = request.args.get('sort_by', 'date')                   # Dropdown menu : Filtre trier selon (date de sortie, note de la presse, note des spectateurs)
    sort_order_request = request.args.get('sort_order', 'descending')       # Dropdown menu : Ordre du tri
    search_query = request.args.get('search_query', '').strip()             # Champ de recherche
    exclude_not_rated = request.args.get('exclude_not_rated') == 'on'       # Checkbox : Exclure films non notés

    # Applique les filtres 
    movies = apply_filters(collection, genre_request, sort_by_request, sort_order_request, exclude_not_rated, search_query)

    all_genres = list(collection.distinct('genre')) # Liste de tous les genres possibles pour les afficher dans le dropdown menu "Filtrer par genre"
    return render_template('index.html', movies=movies, all_genres=all_genres, selected_genre=genre_request, selected_sort_by=sort_by_request, selected_order=sort_order_request, exclude_not_rated=exclude_not_rated)


@app.route('/movie/<movie_id>')
def movie(movie_id):
    """
    Page affichant toutes les informations du film sélectionné.
    """
    movie = collection.find_one({'_id': movie_id})
    return render_template('movie.html', movie=movie)

@app.route('/graphs')
def graphs():
    """
    Page affichant des graphiques pour de la visualisation des données scrapées.
    """
    movies_per_genre_fig = movies_per_genre_graph(collection)               # Bar graph du nombre de film par genre
    mean_ratings_per_genre = mean_ratings_per_genre_graph(collection)       # Bar graph des notes moyennes par genre, de la presse et des spectateurs
    mean_ratings_date = mean_ratings_date_graph(collection)                 # Line graph de l'évolution des notes de la presse et des spectateurs dans le temps 

    return render_template('graphs.html',
                           movies_per_genre_fig=movies_per_genre_fig,
                           mean_ratings_per_genre_fig=mean_ratings_per_genre,
                           mean_ratings_date_fig=mean_ratings_date)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
