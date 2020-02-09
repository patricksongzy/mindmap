from googletrans import Translator
import sys

import tweepy
from tweepy import Stream
from tweepy import StreamListener
from tweepy import OAuthHandler
import json
from geopy.geocoders import GoogleV3

from flask import Flask
from flask_pymongo import PyMongo

from cloud_sentiment import analyze_sentiment
from google.cloud import translate_v2 as translate
translate_client = translate.Client()

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/test"
mongo = PyMongo(app)

consumer_key = ''
consumer_secret = ''

access_token = ''
access_secret = ''

# authentication for api
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

geolocator = GoogleV3(api_key="")

class Listener(StreamListener):
    def __init__(self, output_stream=sys.stdout):
        super(Listener, self).__init__()
        self.output_stream = output_stream
        self.translator = Translator()
    

    def on_status(self, status):
        tweet_text = status.text
        tweet_document = {}
        
        try:
            tweet_text = translate_client.translate(tweet_text, target_language='en')['translatedText']
            tweet_document["translated"] = True
        except json.JSONDecodeError:
            pass

        if (status.coordinates == None):
            if (status.user.location != None):
                print(status.user.location, file=self.output_stream)
                location = geolocator.geocode(status.user.location)
                if (location != None):
                    print(location)
                    tweet_document["user_country"] = (location.longitude, location.latitude)
            else:
                if (status.place != None):
                    print(status.place, file=self.output_stream)
                    place_doc = {}
                    place_doc["country"] = status.place.country
                    place_doc["coordinates"] = status.place.bounding_box.coordinates

                    tweet_document["status_place"] = place_doc

                else:
                    return
        else:
            print(status.coordinates, file=self.output_stream)
            tweet_document["coordinates"] = status.coordinates[0][0]

        print(tweet_text, file=self.output_stream)
        tweet_document["tweet_text"] = tweet_text
        score = analyze_sentiment(tweet_text)
        tweet_document["sentiment_score"] = score[0]
        tweet_document["sentiment_magnitude"] = score[1]

        #json_data = json.dumps(tweet_document)

        print(tweet_document)
        mongo.db.posts.insert_one(tweet_document)

    def on_error(self, status_code):
        print(status_code)
        return False


api = tweepy.API(auth, wait_on_rate_limit=True)

while True:
    listener = Listener()
    stream = Stream(auth=api.auth, listener=listener)

    try:
        stream.sample()
    except KeyboardInterrupt as e:
        print("Stop")
    finally:
        stream.disconnect()
