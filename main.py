#import scrapy
from flask import Flask
from flask_pymongo import PyMongo
from bson.json_util import loads, dumps
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/test"
app.config['CORS_HEADERS'] = 'Content-Type'
mongo = PyMongo(app)

#MongoDB query filters/conditions
sentiment_cond = {"$and": [
    {"sentiment_score": {"$exists": True}},
    {"sentiment_magnitude": {"$exists": True}}]}

coord_cond = {"$or": [
    {"status_place": {"$exists": True}},
    {"user_country": {"$type": "array"}}]}

#Get all posts
@app.route("/posts")
def get_posts():
    posts_payload = mongo.db.posts.find()
    return dumps(posts_payload)

#Get posts with location data
@app.route("/posts-coords")
def get_coord_posts():
    payload = mongo.db.posts.find(coord_cond)
    return dumps(payload)

#Get posts with sentiment data
@app.route("/posts-sentiment")
def get_sentiment_posts():
    payload = mongo.db.posts.find(sentiment_cond)
    return dumps(payload)

#Get useful posts
@app.route("/posts-useful")
def get_useful_posts():
    payload = mongo.db.posts.find({"$and": [sentiment_cond, coord_cond]})
    return dumps(payload)

#Have a query-based moodmap?

if __name__ == '__main__':
    app.run()
