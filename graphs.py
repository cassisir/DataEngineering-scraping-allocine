import plotly.express as px


def movies_per_genre_graph(collection):
    """
    Graphique (bar chart) du nombre de films par genre
    """
    # Regrouper les films par genre
    movies_per_genre_query = [
        {"$unwind": "$genre"},
        {"$group": {"_id": "$genre", "count": {"$sum": 1}}}
    ]
    movies_per_genre = list(collection.aggregate(movies_per_genre_query))
    sorted_movies_per_genre = sorted(movies_per_genre, key=lambda x: x['count']) # Genres ordonnés pour une visualisation plus claire

    genres = [genre["_id"] for genre in sorted_movies_per_genre]
    counts = [genre["count"] for genre in sorted_movies_per_genre]

    fig_movies_per_genre = px.bar(
        x=genres, 
        y=counts, 
        labels={'x':'Genre', 'y':'Count'}, 
        title='Number of Movies per Genre',
        text=counts,
        )
    return fig_movies_per_genre


def mean_ratings_per_genre_graph(collection):
    """
    Graphique des notes moyennes par genre.
    Couleur 1 = press ratings
    Couleur 2 = spectators ratings
    """
    ## PRESS ##
    mean_press_ratings_query = [
        {"$match": {"ratings.press": {"$exists": True, "$ne": "not rated"}}},  # Ne sélectionne pas les films non notés
        {"$unwind": "$genre"},
        {"$group": {"_id": "$genre", "mean_press_rating": {"$avg": {"$toDouble": "$ratings.press"}}}}
    ]

    result_press = list(collection.aggregate(mean_press_ratings_query))

    # Extraction des genres et de leur moyenne selon la press
    genres_press = [genre["_id"] for genre in result_press]
    mean_press_ratings = [genre["mean_press_rating"] for genre in result_press]

    ## SPECTATORS ##
    mean_spectators_ratings_query = [
        {"$match": {"ratings.spectators": {"$exists": True, "$ne": "not rated"}}},  # Ne sélectionne pas les films non notés
        {"$unwind": "$genre"},
        {"$group": {"_id": "$genre", "mean_spectators_ratings": {"$avg": {"$toDouble": "$ratings.spectators"}}}}
    ]
    result_spectators = list(collection.aggregate(mean_spectators_ratings_query))

    # Extraction des genres et de leur moyenne selon les spectateurs
    genres_spectators = [genre["_id"] for genre in result_spectators]
    mean_spectators_ratings = [genre["mean_spectators_ratings"] for genre in result_spectators]

    # Création du graphique
    fig_ratings_per_genre = px.bar(x=genres_press + genres_spectators, 
                y=mean_press_ratings + mean_spectators_ratings,
                color=['Press'] * len(genres_press) + ['Spectators'] * len(genres_spectators),
                labels={'y': 'Note moyenne', 'x': 'Genre', 'color': 'Catégorie note'},
                title='Note moyenne par genre : Press vs Spectators',
                barmode='group')

    return fig_ratings_per_genre


def mean_ratings_date_graph(collection):
    """
    Graphique (line chart) de l'évolution des notes moyennes dans le temps.
    """
    # Ne sélectionne que les films notés
    rated_movies = {
        "$match": {
            "ratings.press": {"$exists": True, "$ne": "not rated"},
            "ratings.spectators": {"$exists": True, "$ne": "not rated"},
            "date": {"$type": "date"}  # Ne sélectionne que les films avec des dates valides
        }
    }

    group_by_date = {
        "$group": {
            "_id": {
                "year": {"$year": "$date"},     # Groupe par année
                "month": {"$month": "$date"}    # Groupe par mois
            },
            "date": {
                "$first": "$date"      # Récupère une seule occurence de chaque date (car elle est la même pour tous les films groupés)
            },
            "mean_press_rating": {"$avg": "$ratings.press"},            # Calcule la moyenne des notes de presse
            "mean_spectators_rating": {"$avg": "$ratings.spectators"}   # Calcule la moyenne des notes des spectateurs
        }
    }

    # Tri par ordre chronologique
    sort = {"$sort": {"date": 1}}

    # Execute the aggregation pipeline
    result = list(collection.aggregate([rated_movies, group_by_date, sort]))

    # Création du graphique
    fig = px.line(result, x="date", y=["mean_press_rating", "mean_spectators_rating"],
                  labels={'value': 'Note moyenne', 'variable': 'Catégorie note', 'date': 'Mois et année'},
                  title='Evolution des Notes Moyennes dans le Temps')

    return fig