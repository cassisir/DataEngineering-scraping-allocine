from pymongo import MongoClient
import matplotlib.pyplot as plt

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.allocine
collection = db.movie_collection

# Aggregate the count of movies per genre
movies_per_genre = [
    {"$unwind": "$genre"},
    {"$group": {"_id": "$genre", "count": {"$sum": 1}}}
]

result = list(collection.aggregate(movies_per_genre))

# Extract genre names and corresponding counts
genres = [entry["_id"] for entry in result]
counts = [entry["count"] for entry in result]

# Plot the bar graph
plt.bar(genres, counts, color='blue')
plt.xlabel('Genre')
plt.ylabel('Number of Movies')
plt.title('Number of Movies per Genre')
plt.xticks(rotation=90, ha='center')
plt.tight_layout()

# Save the plot as an image (PNG format)
plt.savefig('movies_per_genre.png')

# Aggregate the mean press ratings per genre
pipeline = [
    {"$match": {"ratings.press": {"$exists": True, "$ne": "--"}}},  # Filter out movies without press ratings
    {"$unwind": "$genre"},
    {"$group": {"_id": "$genre", "mean_press_rating": {"$avg": {"$toDouble": "$ratings.press"}}}}
]

result = list(collection.aggregate(pipeline))

# Extract genre names and corresponding mean press ratings
genres = [entry["_id"] for entry in result]
mean_press_ratings = [entry["mean_press_rating"] for entry in result]

# Plot the bar graph
plt.bar(genres, mean_press_ratings, color='green')
plt.xlabel('Genre')
plt.ylabel('Mean Press Rating')
plt.title('Mean Press Rating per Genre')

# Rotate the x-axis labels to 90 degrees
plt.xticks(rotation=90, ha='center')  # ha='center' centers the labels on the ticks

plt.tight_layout()

# Save the plot as an image (PNG format)
plt.savefig('mean_press_ratings_per_genre.png')