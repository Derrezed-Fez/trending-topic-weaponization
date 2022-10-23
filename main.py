import pymongo

def main():
    # Create Mongo client and check for db intialization
    mdb = pymongo.MongoClient("mongodb://localhost:27017/")
    dblist = mdb.list_database_names()
    if "topic" not in dblist:
        topic_db = mdb['topic']
    print(topic_db)


if __name__ == '__main__':
    main()
