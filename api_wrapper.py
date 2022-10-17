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
    '''
    Init function: called when the object is instantiated.
    Inputs: None
    Outputs: None
    '''
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

    '''
    Init function: called whn the object is instantiated.
    Inputs: num_trends - type: int - description: the number of trends to pull from the daily trends list
    Outputs: the trends from the US region for the day - type: list of dictionaries
    '''
    def get_daily_trends(self, num_trends):
        g = geocoder.osm("US")
        closest_loc = self.api.closest_trends(g.lat, g.lng)
        trends = self.api.get_place_trends(closest_loc[0]["woeid"])
        return trends[0]["trends"][0:num_trends]

'''
A wrapper for the Google API.
Use to grab current daily trends for Google searches.
'''
class GoogleWrapper():
    '''
    Init function: called whn the object is instantiated.
    Inputs: None
    Outputs: None
    '''
    def __init__(self):
        self.api = TrendReq()

    '''
    Init function: called when the object is instantiated.
    Inputs: num_trends - type: int - description: the number of trends to pull from the daily trends list
    Outputs: the trends from the US region for the day - type: list of dictionaries
    '''
    def get_daily_trends(self, num_trends):
        trends = self.api.today_searches(pn='US')
        return trends.head(num_trends)

wrapper = TwitterWrapper()
print(wrapper.get_daily_trends(20))

# wrapper = GoogleWrapper()
# Pull the top 20 trends for the day
# print(wrapper.get_daily_trends(20))
