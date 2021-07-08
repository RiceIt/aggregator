import pymongo
import psycopg2
import slugify

from parser.parser import AbstractBuilder, FlBuilder, FreelanceBuilder, HabrBuilder
from telegram_bot.config import Configuration
from telegram_bot.funcs import send_message
from telegram_bot.logger import logger


mongo = pymongo.MongoClient(Configuration.MONGODB_URI)
db = mongo["tasks"]


def is_id_exists(platform, _id):
    collection = db[platform]
    document = collection.find_one({"_id": _id})
    if document:
        return True
    return False


def insert_one(task):
    collection = db[task["platform"]]
    collection.insert_one(task)


def _add_filter(conn, cur, name, slug, platform):
    cur.execute(f"INSERT INTO filters (name, slug, platform) VALUES (%s, %s, %s)", (name, slug, platform))
    conn.commit()
    logger.info(f'Добавлена новая категория: "{platform}: {name}"')


# def add_categories_if_not_exist(filters, platform):
    # conn = psycopg2.connect(f"dbname={Configuration.POSTGRESQL_DBNAME} "
    #                         f"user={Configuration.POSTGRESQL_USER} "
    #                         f"password={Configuration.POSTGRESQL_PASSWORD}")
    #
    # cur = conn.cursor()
    # for filter_name in filters:
    #     filter_slug = slugify.slugify(filter_name)
    #     try:
    #         _add_filter(conn, cur, filter_name, filter_slug, platform)
    #
    #     except psycopg2.errors.UniqueViolation:
    #         cur.execute("ROLLBACK")
    #         conn.commit()
    # cur.close()
    # conn.close()


def push_notifications(task):
    message = f"📌 <b>{task['title']}</b>\n\n📝 {task['description']}\n\n💰 {task['price']}\n\n" \
              f"📚 {' '.join(task['categories'])}\n\n🔗 {task['url']}"
    conn = psycopg2.connect(f"dbname={Configuration.POSTGRESQL_DBNAME} "
                            f"user={Configuration.POSTGRESQL_USER} "
                            f"password={Configuration.POSTGRESQL_PASSWORD}")

    categories_placeholders = ', '.join(['%s'] * len(task['categories']))
    sql = f"SELECT users.chat_id, users.silent_mode FROM filters INNER JOIN user_filters ON (filters.name IN ({categories_placeholders}) AND filters.platform = (%s) AND user_filters.filter_id = filters.id) INNER JOIN users ON (users.id = user_filters.user_id AND users.is_active = True) GROUP BY users.chat_id, users.silent_mode"

    cur = conn.cursor()
    cur.execute(sql, (*task['categories'], task['platform']))
    users = cur.fetchall()
    for user in users:
        chat_id, silent_mode = user
        send_message(chat_id, text=message, parse_mode='html', disable_notification=silent_mode)


def create_task_if_not_exists(builder: AbstractBuilder):
    builder.add_id()
    builder.add_platform()
    exists = builder.exists()
    if exists:
        return None
    builder.add_title()
    builder.add_url()
    builder.add_description()
    builder.add_created_at()
    builder.add_price()
    builder.add_categories()
    return builder.task


def main():
    platforms = (
        FlBuilder, FreelanceBuilder, HabrBuilder,
    )

    for platform in platforms:
        tasks_soup_list = platform.get_task_list()
        for task_soup in tasks_soup_list:
            created, task = create_task_if_not_exists(platform(task_soup))
            if created:
                insert_one(task)
                push_notifications(task)

