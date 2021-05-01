import pymongo


MONGODB_URI = 'mongodb://localhost:27017/'

mongo = pymongo.MongoClient(MONGODB_URI)
db = mongo["tasks"]
categories_collection = db['categories']


def get_categories():
    categories_collection.find({})

    for category in categories_collection.find({}):
        print(category)


get_categories()
