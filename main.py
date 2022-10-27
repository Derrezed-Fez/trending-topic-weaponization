import pymongo
import time
from api_wrapper import TwitterWrapper, GoogleWrapper, VirusTotalWrapper
from datetime import datetime
from bson.objectid import ObjectId

def main():
    # Create Mongo client and check for db intialization
    mdb = pymongo.MongoClient("mongodb://localhost:27017/")
    topic_db = mdb['topic']
    twitterTrendsCollection = topic_db['twitter_trends']
    googleTrendsCollection = topic_db['google_trends']

    twitterApi = TwitterWrapper()
    googleApi = GoogleWrapper()
    virusTotalApi = VirusTotalWrapper()

    twitResults = twitterApi.get_daily_trends(20)
    googleResult = googleApi.get_daily_trends(20)
    for item in twitResults:
        item['name'] = item['name'].replace('#', '').replace(' ', '')
    twitter_ids = twitterTrendsCollection.insert_many([{'results': twitResults, 'time': str(datetime.now())}])
    google_ids = googleTrendsCollection.insert_many([{'results': [{'name': result} for result in googleResult], 'time': str(datetime.now())}])
    virusTotalCollection = topic_db['virus_total_results']
    virusReportResults = virusTotalApi.get_relevant_data([keyword['name'] for keyword in twitResults])
    virusTotalCollection.insert_many([{'results': virusReportResults, 'origin': twitter_ids.inserted_ids[0]}])
    virusReportResults = virusTotalApi.get_relevant_data(googleResult)
    virusTotalCollection.insert_many([{'results': virusReportResults, 'origin': google_ids.inserted_ids[0]}])

if __name__ == '__main__':
    main()
