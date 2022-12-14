import os
import tweepy
from dotenv import load_dotenv
import geocoder
import pandas as pd
from pytrends.request import TrendReq
import vt
import time
from logger import Logger
from twilio.rest import Client
from googlesearch import search
import requests

'''
Class to wrap the Twitter API. Use to grab trends and perform other actions on Twitter. API Keys and other info stored in a dotenv file.
Work in Progress. Need elevated API permissions to finish implementing
'''


class TwitterWrapper():
    '''
    Init function: called when the object is instantiated.
    Inputs: logger - type: Logger - Description: The logger wrapper to log events to.
    Outputs: None
    '''

    def __init__(self, logger:Logger, twilio_client:Client):
        consumer_key = os.environ["app_key"]
        consumer_secret = os.environ["app_secret"]
        access_token = os.environ["access_token"]
        access_token_secret = os.environ["access_secret"]
        self.logger = logger

        auth = tweepy.OAuth1UserHandler(
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret
        )

        self.api = tweepy.API(auth)
        self.twilio_client = twilio_client

    '''
    get_daily_trends. Used to get a number of daily trends in Google searches.
    Inputs: num_trends - type: int - description: the number of trends to pull from the daily trends list
    Outputs: the trends from the US region for the day - type: list of dictionaries
    '''

    def get_daily_trends(self, num_trends):
        try:
            g = geocoder.osm("US")
        except Exception as e:
            self.logger.log_error('Grabbing US geocoder location failed. Trace: ' + str(e))
            try:
                self.twilio_client.messages.create(body='FAILURE: ' + str(e), from_='+16802197947', to='INSERT PHONE NUMBER HERE')
            except Exception as ex:
                self.logger.log_error('Error sending SMS- ' + str(ex))
        try:
            closest_loc = self.api.closest_trends(g.lat, g.lng)
            trends = self.api.get_place_trends(closest_loc[0]["woeid"])
        except Exception as e:
            self.logger.log_error('Collecting closest trends from Twitter API failed. Trace: ' + str(e))
            try:
                self.twilio_client.messages.create(body='FAILURE: ' + str(e), from_='+16802197947', to='INPUT PHONE NUMBER HERE')
            except Exception as ex:
                self.logger.log_error('Error sending SMS- ' + str(ex))
        return trends[0]["trends"][0:num_trends]


'''
A wrapper for the Google API.
Use to grab current daily trends for Google searches.
'''


class GoogleWrapper():
    '''
    Init function: called whn the object is instantiated.
    Inputs: logger - type: Logger - Description: The logger wrapper to log events to.
    Outputs: None
    '''
    def __init__(self, logger:Logger, twilio_client:Client):
        self.api = TrendReq()
        self.logger = logger
        self.twilio_client = twilio_client

    '''
    get_daily_trends. Used to get a number of daily trends in Google searches.
    Inputs: num_trends - type: int - description: the number of trends to pull from the daily trends list
    Outputs: the trends from the US region for the day - type: list of dictionaries
    '''
    def get_daily_trends(self, num_trends):
        try:
            trends = [result[1] for result in self.api.realtime_trending_searches(pn='US')[0:num_trends].to_numpy()]
        except Exception as e:
            self.logger.log_error('Collecting Google API trending searches failed. Trace: ' + str(e))
            try:
                self.twilio_client.messages.create(body='FAILURE: ' + str(e), from_='+16802197947', to='INPUT PHONE NUMBER HERE')
            except Exception as ex:
                self.logger.log_error('Error sending SMS- ' + str(ex))
        keywords = list()
        for trend in trends:
            for keyword in trend:
                keywords.append(keyword)
        self.common_keywords = list()
        self.trend_counter = 1
        self.__get_most_common(trends=keywords, num_trends=num_trends)
        return self.common_keywords

    '''
    __get_most_common. Recursive private function to find the most common out of all keywords.
    Inputs: trends - type: list - description: the new trends list to process. num_trends - type: int - description: the number of trends to collect.
    Outputs: None, appends all new finds to global class property.
    '''
    def __get_most_common(self, trends:list, num_trends:int):
        common = max(set(trends), key=trends.count)
        self.common_keywords.append(common.replace(' ', ''))
        self.trend_counter += 1
        new_keywords = list()
        for item in trends:
            if item != common:
                new_keywords.append(item)
        if self.trend_counter <= num_trends:
            self.__get_most_common(new_keywords, num_trends)
        return

'''
A wrapper for the Virus Total API.
Used to lookup malicious URLs, EXEs, and other potentially harmful vectors of attack.
'''
class VirusTotalWrapper():
    '''
    Init function: called whn the object is instantiated.
    Inputs: logger - type: Logger - Description: The logger wrapper to log events to.
    Outputs: None
    '''

    def __init__(self, logger:Logger, twilio_client:Client, search_google:bool=True, search_bing:bool=True):
        api_key = os.environ['virus_total_key']
        self.api = vt.Client(api_key)
        self.logger = logger
        self.twilio_client = twilio_client
        self.azure_api_key = os.environ['azure_api_key']
        self.search_google = search_google
        self.search_bing = search_bing

    '''
    get_relevsant_data - Used to query Virus Total to see if a series of artifacts are suspicious.
    Inputs: keywords - type: list - description: the keywords to use to generate suspicious artifacts
    Outputs: A list of all artifacts that were flagged by Virus Total
    '''

    def get_relevant_data(self, keywords):
        urls = list()
        while len(urls) < 500:
            for keyword in keywords:
                if self.search_google:
                    for url in self.google_search(keyword):
                        urls.append(url)
                if self.search_bing:
                    for url in self.bing_search(keyword):
                        for result in url["webPages"]["value"]:
                            urls.append(result)
        flagged = dict()
        for url in urls:
            url_id = vt.url_id(url)
            try:
                flagged[url] = self.api.get_object('/urls/{}', url_id).last_analysis_stats
            except Exception as e:
                self.logger.log_error('Collecting URL results from Virus Total API failed. Trace: ' + str(e))
                try:
                    if 'NotFoundError' not in str(e):
                        self.twilio_client.messages.create(body='FAILURE: ' + str(e), from_='+16802197947', to='INPUT PHONE NUMBER HERE')
                    else:
                        flagged[url] = 'URL Does Not Exist'
                except Exception as ex:
                    self.logger.log_error('Error sending SMS- ' + str(ex))
            time.sleep(15)
        return flagged
    
    '''
    Google_search
    Google searches 10 keywords at a time in batches based on keywork input.
    '''
    def google_search(self, keyword):
        return search(keyword, tld="co.in", num=10, stop=10, pause=2)

    '''
    bing_search
    Bing searches keyword at a time in batches based on keywork input.
    '''
    def bing_search(self, keyword):
        headers = {"Ocp-Apim-Subscription-Key": self.azure_api_key}
        params = {"q": keyword, "textDecorations": True, "textFormat": "HTML"}
        response = requests.get("https://api.bing.microsoft.com/v7.0/search", headers=headers, params=params)
        response.raise_for_status()
        return response.json()
