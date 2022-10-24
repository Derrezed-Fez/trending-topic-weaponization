import pymongo
import time
from api_wrapper import TwitterWrapper, GoogleWrapper, VirusTotalWrapper

def main():
    # Create Mongo client and check for db intialization
    # mdb = pymongo.MongoClient("mongodb://localhost:27017/")
    # dblist = mdb.list_database_names()
    # if "topic" not in dblist:
    #     topic_db = mdb['topic']
    # print(topic_db)

    twitterApi = TwitterWrapper()
    googleApi = GoogleWrapper()
    virusTotalApi = VirusTotalWrapper()

    while True:
        twitResults = twitterApi.get_daily_trends(5)
        googleResult = googleApi.get_daily_trends(5)
        # print(googleResult)
        # print(twitResults)
        time.sleep(5)

        twitNameList = ["Russ", "Rypien", "McManus"]
        virusReportResults = virusTotalApi.get_relevant_data(twitNameList)
        print(virusReportResults)







if __name__ == '__main__':
    main()
