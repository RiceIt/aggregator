import pymongo
import datetime
import slugify

from pymongo.errors import DuplicateKeyError
from wtforms import BooleanField, SubmitField


MONGODB_URI = 'mongodb://localhost:27017/'

mongo = pymongo.MongoClient(MONGODB_URI)
db = mongo["tasks"]
tasks_collection = db['tasks']
categories_collection = db['categories']


def get_tasks():
    tasks = tasks_collection.find({})

    for task in tasks:
        print(task)


def insert_one_if_not_exist(task):
    try:
        tasks_collection.insert_one(task)
        print(f"Успешно добавлено: {task['_id']}, {task['created_at']}")
        return False
    except DuplicateKeyError:
        return True


def update_one(_id, categories):
    tasks_collection.update_one({'_id': _id}, {'$set': {'categories': categories}})


def add_categories_if_not_exist(categories):
    for category in categories:
        category_name = slugify.slugify(category)
        print(category_name)
        try:
            categories_collection.insert_one({'_id': category_name, 'category': category})
        except DuplicateKeyError:
            pass


def get_category_form_attributes():
    result = {}
    categories = categories_collection.find({})
    for category in categories:
        result[category['_id']] = BooleanField(category["category"])
    return result
