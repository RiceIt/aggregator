import pymongo
import datetime

from pymongo.errors import DuplicateKeyError


MONGODB_URI = 'mongodb://localhost:27017/'

mongo = pymongo.MongoClient(MONGODB_URI)
db = mongo["tasks"]
tasks_collection = db['tasks']


def get_tasks():
    tasks = tasks_collection.find({})

    for task in tasks:
        print(task)


def insert_one_if_not_exist(task):
    try:
        tasks_collection.insert_one(task)
        return f"Успешно добавлено: {task['_id']}, {task['created_at']}"
    except DuplicateKeyError:
        return "Запись уже существует"
