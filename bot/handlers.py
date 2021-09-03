from bot.funcs import (send_start_message, send_platforms_list, send_platform_categories_list, update_category,
                       answer_callback_query, send_platforms_message, notifications_message_handler,
                       notifications_callback_handler, update_time)
from db.models import add_user, create_times


def request_handler(data):
    if data.get("message"):
        message_handler(data)
    elif data.get("callback_query"):
        callback_handler(data)


def message_handler(data):
    if data["message"]["text"] == "/start":
        user_id = add_user(chat_id=data["message"]["chat"]["id"])
        if user_id:
            create_times(user_id)
        send_start_message(chat_id=data["message"]["chat"]["id"])
    elif data["message"]["text"] == "Настроить категории":
        send_platforms_message(chat_id=data["message"]["chat"]["id"])
    elif data["message"]["text"] == "Настроить время":
        chat_id = data["message"]["chat"]["id"]
        notifications_message_handler(chat_id=chat_id)


def callback_handler(data):
    if data["callback_query"]["data"] == "start":
        select_platforms_handler(data)
    elif data["callback_query"]["data"].startswith("p:"):
        platform_handler(data)
    elif data["callback_query"]["data"].startswith("c:"):
        category_handler(data)
    elif data["callback_query"]["data"].startswith("t:p:"):
        chat_id = data["callback_query"]["message"]["chat"]["id"]
        message_id = data["callback_query"]["message"]["message_id"]
        _, _, page = data["callback_query"]["data"].split(":")
        notifications_callback_handler(chat_id=chat_id, message_id=message_id, page=page)
    elif data["callback_query"]["data"].startswith("t:"):
        time_handler(data)
    answer_callback_query(data["callback_query"]["id"])


def select_platforms_handler(data):
    chat_id = data["callback_query"]["message"]["chat"]["id"]
    message_id = data["callback_query"]["message"]["message_id"]
    send_platforms_list(chat_id=chat_id, message_id=message_id)


def platform_handler(data):
    chat_id = data["callback_query"]["message"]["chat"]["id"]
    message_id = data["callback_query"]["message"]["message_id"]
    _, platform, page = data["callback_query"]["data"].split(":")
    send_platform_categories_list(chat_id=chat_id, message_id=message_id, platform=platform, page=int(page))


def category_handler(data):
    chat_id = data["callback_query"]["message"]["chat"]["id"]
    message_id = data["callback_query"]["message"]["message_id"]
    callback_query_id = data["callback_query"]["id"]
    _, platform, category_id, page = data["callback_query"]["data"].split(":")
    update_category(chat_id=chat_id, message_id=message_id, platform=platform,
                    category_id=category_id, page=int(page), callback_query_id=callback_query_id)


def time_handler(data):
    chat_id = data["callback_query"]["message"]["chat"]["id"]
    message_id = data["callback_query"]["message"]["message_id"]
    _, time_hour = data["callback_query"]["data"].split(":")
    page = int(time_hour) // 16 + 1
    update_time(chat_id=chat_id, time_hour=time_hour)
    notifications_callback_handler(chat_id=chat_id, message_id=message_id, page=page)
