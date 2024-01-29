from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.allocine
collection = db.movie_collection

@app.route('/')
def index():
    movies = list(collection.find())
    return render_template('index.html', movies=movies)

@app.route('/movie/<title>')
def movie(title):
    movie = collection.find_one({'title': title})
    return render_template('movie.html', movie=movie)

# @app.route('/')
# def accueil():
#     return "Presentation"
# @app.route('/film/<string:movie_name>')
# def presentation_film(movie_name: str):
#     # Retrieve all movies from the MongoDB collection
#     return f"Titre : {movie_name}"
#     # movies = list(collection.find())
#     # return render_template('index.html', movies=movies)

if __name__ == '__main__':
    app.run(debug=True)
