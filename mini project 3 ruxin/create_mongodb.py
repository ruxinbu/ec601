def connect_to_mongodb():
    import pymongo
    import pprint
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = client.twitterapi
    return mydb