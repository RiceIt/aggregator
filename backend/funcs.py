import pymongo
import datetime

from backend.app import app, db
from backend.models import User


def get_tasks():
    mongo = pymongo.MongoClient(app.config['MONGODB_URI'])
    db = mongo["tasks"]
    tasks_collection = db['tasks']
    tasks = tasks_collection.find().sort("created_at", -1)

    return tasks


def add_user():
    u = User(psw='thuiehguei8gh7eh', date=datetime.datetime.now())
    db.session.add(u)
    db.session.commit()


def get_users():
    users = User.query.all()
    return users