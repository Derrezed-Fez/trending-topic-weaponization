import pymongo
import time
from api_wrapper import TwitterWrapper, GoogleWrapper, VirusTotalWrapper
from datetime import datetime
from bson.objectid import ObjectId
from logger import Logger
from twilio.rest import Client
import os

def main():
    log_wrapper = Logger(str(datetime.now()))
    # Send update using Twilio
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)
    try:
        client.messages.create(body='Starting Data Collection at ' + str(datetime.now()), from_='+16802197947', to='INPUT PHONE NUMBER HERE')
    except Exception as e:
        log_wrapper.log_error('Error sending SMS update: ' + str(e))
    # Create Mongo client and check for db intialization
    mdb = pymongo.MongoClient("mongodb://localhost:27017/")
    log_wrapper.log_info('Started Mongo Client at mongodb://localhost:27017')
    topic_db = mdb['topic']
    twitterTrendsCollection = topic_db['twitter_trends']
    googleTrendsCollection = topic_db['google_trends']
    virusTotalCollection = topic_db['virus_total_results']
    log_wrapper.log_info('Created Topic DB and collections for: twitter_trends, google_trends, virus_total_results')

    # Initialize our API Wrappers for pulling our trends and testing malicious URLs
    twitterApi = TwitterWrapper(logger=log_wrapper, twilio_client=client)
    googleApi = GoogleWrapper(logger=log_wrapper, twilio_client=client)
    virusTotalApi = VirusTotalWrapper(logger=log_wrapper, twilio_client=client, search_bing=False, search_google=True)

    # Get 20 highest trending keywords from each source
    twitResults = twitterApi.get_daily_trends(20)
    log_wrapper.log_info('Grabbed 20 daily keywords from Twitter')
    googleResult = googleApi.get_daily_trends(20)
    log_wrapper.log_info('Grabbed 20 daily keywords from Google')
    for item in twitResults:
        item['name'] = item['name'].replace('#', '').replace(' ', '')
    # Insert trends into the DB
    twitter_ids = twitterTrendsCollection.insert_many([{'results': twitResults, 'time': str(datetime.now())}])
    google_ids = googleTrendsCollection.insert_many([{'results': [{'name': result} for result in googleResult], 'time': str(datetime.now())}])
    log_wrapper.log_info('Inserted Twitter and Google Keywords into DB')

    # Generate malicious URLs based on keywords and scan for malicious results. Insert these results into the DB
    virusReportResults = virusTotalApi.get_relevant_data([keyword['name'] for keyword in twitResults])
    virusTotalCollection.insert_many([{'results': virusReportResults, 'origin': twitter_ids.inserted_ids[0]}])
    virusReportResults = virusTotalApi.get_relevant_data(googleResult)
    virusTotalCollection.insert_many([{'results': virusReportResults, 'origin': google_ids.inserted_ids[0]}])
    log_wrapper.log_info('Inserted Twitter and Google malicious URL results into DB')
    log_wrapper.close_logfile()
    try:
        client.messages.create(body='Ending Data Collection at ' + str(datetime.now()), from_='+16802197947', to='INPUT PHONE NUMBER HERE')
    except Exception as e:
        log_wrapper.log_error('Error sending SMS update: ' + str(e))

if __name__ == '__main__':
    main()
