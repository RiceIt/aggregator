import pymongo
import psycopg2
import datetime
import slugify

from pymongo.errors import DuplicateKeyError
from wtforms import BooleanField, SubmitField
from backend.config import Configuration
from telegram_bot.funcs import send_message

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


def add_filter(conn, cur, name, slug):
    cur.execute(f"INSERT INTO filters (name, slug) VALUES (%s, %s)", (name, slug))
    conn.commit()
    print("Успешно!")


# def add_categories_if_not_exist(categories):
#     for category in categories:
#         category_name = slugify.slugify(category)
#         print(category_name)
#         try:
#             categories_collection.insert_one({'_id': category_name, 'category': category})
#         except DuplicateKeyError:
#             pass


def add_filters_if_not_exist(filters):
    conn = psycopg2.connect(f"dbname={Configuration.POSTGRESQL_DBNAME} "
                            f"user={Configuration.POSTGRESQL_USER} "
                            f"password={Configuration.POSTGRESQL_PASSWORD}")

    cur = conn.cursor()
    for filter_name in filters:
        filter_slug = slugify.slugify(filter_name)
        try:
            add_filter(conn, cur, filter_name, filter_slug)
        except psycopg2.errors.UniqueViolation:
            cur.execute("ROLLBACK")
            conn.commit()
    cur.close()
    conn.close()


def push_notifications(task, categories):
    print(task)
    print(categories)
    message = f"{task['title']}\n\n{task['text']}\n\n{task['price']}\n\n{' '.join(categories)}\n\n{task['link']}"
    conn = psycopg2.connect(f"dbname={Configuration.POSTGRESQL_DBNAME} "
                            f"user={Configuration.POSTGRESQL_USER} "
                            f"password={Configuration.POSTGRESQL_PASSWORD}")

    categories_placeholders = ', '.join(['%s'] * len(categories))
    sql = f"SELECT users.chat_id FROM filters INNER JOIN user_filters ON (filters.name IN ({categories_placeholders}) AND user_filters.filter_id = filters.id) INNER JOIN users ON (users.id = user_filters.user_id AND users.is_active = True) GROUP BY users.chat_id"

    cur = conn.cursor()
    cur.execute(sql, categories)
    users = cur.fetchall()
    chat_ids = [u[0] for u in users]
    print(chat_ids)
    for chat_id in chat_ids:
        send_message(chat_id, text=message)


def get_category_form_attributes():
    result = {}
    categories = categories_collection.find({})
    for category in categories:
        result[category['_id']] = BooleanField(category["category"])
    return result
