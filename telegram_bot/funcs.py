import json
import os
import requests

from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy import distinct
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.exc import IntegrityError

from telegram_bot.models import db, Users, Filters


def start(chat_id):
    text = "Сейчас у Вас нет активных категорий! Чтобы бот начал работу, " \
           "подпишитесь на категории, с помощью кнопок внизу"

    u = Users.query.filter_by(chat_id=chat_id).first()

    try:
        filters = u.filters
    except AttributeError:
        u = Users(chat_id=chat_id, is_active=True, date=datetime.now())
        db.session.add(u)
        db.session.commit()
        u = Users.query.filter_by(chat_id=chat_id).first()
        filters = u.filters
    if u.is_active:
        if u.silent_mode:
            keyboard_buttons = [["Удалить категории", "Добавить категории"], ["Отключить беззвучный режим", "Отключить уведомления"]]
        else:
            keyboard_buttons = [["Удалить категории", "Добавить категории"], ["Включить беззвучный режим", "Отключить уведомления"]]
    else:
        keyboard_buttons = [["Удалить категории", "Добавить категории"], ["Включить уведомления"]]

    if filters:
        text = "Категории на которые вы подписаны: " + ", ".join([f"<b><i>{f.name}</i></b>" for f in filters])

    reply_markup = json.dumps({"keyboard": keyboard_buttons, "resize_keyboard": True})
    send_message(chat_id, text=text, parse_mode='html', reply_markup=reply_markup)


def send_message(chat_id, **kwargs):
    method = "sendMessage"
    token = os.environ["TOKEN"]
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, **kwargs}
    response = requests.post(url, data=data)
    if response.status_code in (400, 403):
        u = Users.query.filter_by(chat_id=chat_id).first()
        u.is_active = False
        u.silent_mode = False
        db.session.commit()
    print(response.status_code)


def activate(chat_id):
    u = Users.query.filter_by(chat_id=chat_id).first()
    u.is_active = True
    u.silent_mode = False
    db.session.commit()
    text = "Уведомления включены"
    keyboard_buttons = [["Удалить категории", "Добавить категории"], ["Включить беззвучный режим", "Отключить уведомления"]]
    reply_markup = json.dumps({"keyboard": keyboard_buttons, "resize_keyboard": True})
    send_message(chat_id, text=text, parse_mode='html', reply_markup=reply_markup)


def deactivate(chat_id):
    u = Users.query.filter_by(chat_id=chat_id).first()
    u.is_active = False
    u.silent_mode = False
    db.session.commit()
    text = "Уведомления отключены"
    keyboard_buttons = [["Удалить категории", "Добавить категории"], ["Включить уведомления"]]
    reply_markup = json.dumps({"keyboard": keyboard_buttons, "resize_keyboard": True})
    send_message(chat_id, text=text, parse_mode='html', reply_markup=reply_markup)


def silent_mode_on(chat_id):
    u = Users.query.filter_by(chat_id=chat_id).first()
    u.is_active = True
    u.silent_mode = True
    db.session.commit()
    text = "Беззвучный режим включен"
    keyboard_buttons = [["Удалить категории", "Добавить категории"], ["Отключить беззвучный режим", "Отключить уведомления"]]
    reply_markup = json.dumps({"keyboard": keyboard_buttons, "resize_keyboard": True})
    send_message(chat_id, text=text, parse_mode='html', reply_markup=reply_markup)


def silent_mode_off(chat_id):
    u = Users.query.filter_by(chat_id=chat_id).first()
    u.is_active = True
    u.silent_mode = False
    db.session.commit()
    text = "Беззвучный режим отключен"
    keyboard_buttons = [["Удалить категории", "Добавить категории"], ["Включить беззвучный режим", "Отключить уведомления"]]
    reply_markup = json.dumps({"keyboard": keyboard_buttons, "resize_keyboard": True})
    send_message(chat_id, text=text, parse_mode='html', reply_markup=reply_markup)


def add_platforms(chat_id):
    u = Users.query.filter_by(chat_id=chat_id).first()
    u.adding_filters = True
    db.session.commit()

    platforms = Filters.query.with_entities(Filters.platform).distinct().all()
    platforms = [p[0] for p in platforms]
    platforms.insert(0, "Вернуться")
    keyboard_buttons = get_keyboard_button(platforms)
    reply_markup = json.dumps({"keyboard": keyboard_buttons, "resize_keyboard": True})
    text = "Выберите платформу"
    send_message(chat_id, text=text, reply_markup=reply_markup)


def remove_platforms(chat_id):
    u = Users.query.filter_by(chat_id=chat_id).first()
    u.adding_filters = False
    db.session.commit()

    filters = u.filters
    if filters:
        platforms = list({f.platform for f in filters})
        platforms.insert(0, "Вернуться")
        keyboard_buttons = get_keyboard_button(platforms)
        reply_markup = json.dumps({"keyboard": keyboard_buttons, "resize_keyboard": True})
        text = "Выберите платформу"
        send_message(chat_id, text=text, reply_markup=reply_markup)
    else:
        start(chat_id)


def add_filters(chat_id, text="Выберите категорию, которую хотите добавить"):
    u = Users.query.filter_by(chat_id=chat_id).first()
    u.adding_filters = True
    u.current_platform = "fl.ru"
    db.session.commit()

    res = Filters.query.all()
    filters = [f.name for f in res]
    filters.insert(0, "<< К платформам")
    keyboard_buttons = get_keyboard_button(filters)
    reply_markup = json.dumps({"keyboard": keyboard_buttons, "resize_keyboard": True})
    send_message(chat_id, text=text, reply_markup=reply_markup)


def add_filter(chat_id, category):
    u = Users.query.filter_by(chat_id=chat_id).first()
    f = Filters.query.filter_by(name=category).first()
    try:
        u.filters.append(f)
        db.session.add(u)
        db.session.commit()
        add_filters(chat_id, text=f"Вы подписались на категорию \"{category}\"")
    except FlushError:
        send_message(chat_id, text="Такой категории не существует")


def remove_filters(chat_id, text="Выберите категории, которые хотите удалить"):
    u = Users.query.filter_by(chat_id=chat_id).first()
    u.adding_filters = False
    u.current_platform = "fl.ru"
    db.session.commit()

    filters = u.filters
    if filters:
        filters = [f.name for f in filters]
        filters.insert(0, "<< К платформам")
        keyboard_buttons = get_keyboard_button(filters)
        reply_markup = json.dumps({"keyboard": keyboard_buttons, "resize_keyboard": True})
        send_message(chat_id, text=text, reply_markup=reply_markup)
    else:
        start(chat_id)


def remove_filter(chat_id, category):
    u = Users.query.filter_by(chat_id=chat_id).first()
    f = Filters.query.filter_by(name=category).first()
    try:
        u.filters.remove(f)
        db.session.commit()
        remove_filters(chat_id, f"Вы отписались от категории \"{category}\"")
    except ValueError:
        send_message(chat_id, text="Вы не подписаны на эту категорию")


def to_platforms(chat_id):
    u = Users.query.filter_by(chat_id=chat_id).first()
    adding_filters = u.adding_filters
    if adding_filters:
        add_platforms(chat_id)
    else:
        remove_platforms(chat_id)


def get_users():
    return Users.query.all()


def adding_filter(chat_id):
    return Users.query.filter_by(chat_id=chat_id).first().adding_filters


def get_keyboard_button(buttons):
    result = []
    row = []
    for i, button in enumerate(buttons):
        if i % 2 == 1:
            result.append(row)
            row = [button, ]
        else:
            row.append(button)
    result.append(row)
    print(result)
    return result
