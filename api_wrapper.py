import os
import tweepy
from dotenv import load_dotenv
import geocoder
import pandas as pd
from pytrends.request import TrendReq

'''
Class to wrap the Twitter API. Use to grab trends and perform other actions on Twitter. API Keys and other info stored in a dotenv file.
Work in Progress. Need elevated API permissions to finish implementing
'''
class TwitterWrapper():
    def __init__(self):
        consumer_key = os.environ["app_key"]
        consumer_secret = os.environ["app_secret"]
        access_token = os.environ["access_token"]
        access_token_secret = os.environ["access_secret"]

        auth = tweepy.OAuth1UserHandler(
        consumer_key, 
        consumer_secret, 
        access_token, 
        access_token_secret
        )

        self.api = tweepy.API(auth)
        loc = geocoder.osm("US")
        # print(self.api.closest_trends(loc.lat, loc.lng))
        print(self.api.available_trends())

'''
A wrapper for the Google API.
Use to grab current daily trends for Google searches.
'''
class GoogleWrapper():
    def __init__(self):
        self.api = TrendReq()

    def get_daily_trends(self, num_trends):
        trends = self.api.today_searches(pn='US')
        return trends.head(num_trends)

# wrapper = TwitterWrapper()

wrapper = GoogleWrapper()
# Pull the top 20 trends for the day
print(wrapper.get_daily_trends(20))
