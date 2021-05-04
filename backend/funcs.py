import pymongo

from backend.app import app


def get_tasks():
    mongo = pymongo.MongoClient(app.config['MONGODB_URI'])
    db = mongo["tasks"]
    tasks_collection = db['tasks']
    tasks = tasks_collection.find().sort("created_at", -1)

    return tasks
