from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.allocine
collection = db.movie_collection

@app.route('/')
def index():
    # Retrieve all movies from the MongoDB collection
    movies = list(collection.find())
    return render_template('index.html', movies=movies)

if __name__ == '__main__':
    app.run(debug=True)
