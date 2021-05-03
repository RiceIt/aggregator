import json
import os
from datetime import datetime

from werkzeug.security import generate_password_hash
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.exc import IntegrityError

from telegram_bot.models import db, Users, Filters
import requests


def start(chat_id):
    welcome = "Сейчас у Вас нет активных категорий, чтобы бот начал работу добавтье категории, " \
              "на которые хотите подписаться с помощью кнопок внизу"
    keyboard_buttons = [["Активировать уведомления", "Деактивировать"], ["Удалить категории", "Добавить категории"]]

    u = Users.query.filter_by(chat_id=chat_id).first()

    try:
        filters = u.filters
    except AttributeError:
        u = Users(chat_id=chat_id, is_active=True, date=datetime.now())
        db.session.add(u)
        db.session.commit()
        u = Users.query.filter_by(chat_id=chat_id).first()
        filters = u.filters
    if filters:
        welcome = "Категории на которые вы подписаны: " + ", ".join([f"<i>{f.name}</i>" for f in filters])

    reply_markup = json.dumps({"keyboard": keyboard_buttons, "resize_keyboard": True})
    send_message(chat_id, text=welcome, parse_mode='html', reply_markup=reply_markup)


def send_message(chat_id, **kwargs):
    method = "sendMessage"
    token = os.environ["TOKEN"]
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, **kwargs}
    response = requests.post(url, data=data)
    if response.status_code in (400, 403):
        deactivate(chat_id)
    print(type(response.status_code))


def activate(chat_id):
    u = Users.query.filter_by(chat_id=chat_id).first()
    print(u)
    print(u.chat_id)
    if u.is_active:
        return "Уведомления уже активированы!"
    u.is_active = True
    db.session.commit()
    return "Уведомления активированы!"


def deactivate(chat_id):
    u = Users.query.filter_by(chat_id=chat_id).first()
    print(u)
    print(u.chat_id)
    if not u.is_active:
        return "Уведомления уже отключены!"
    u.is_active = False
    db.session.commit()
    return "Уведомления отключены!"


def add_filters(chat_id, text="Выберите категорию, которую хотите добавить"):
    u = Users.query.filter_by(chat_id=chat_id).first()
    u.adding_filters = True
    db.session.commit()

    filters = Filters.query.all()
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


def adding_filter(chat_id):
    return Users.query.filter_by(chat_id=chat_id).first().adding_filters


def get_keyboard_button(buttons):
    result = []
    row = ["Назад"]
    for i, button in enumerate(buttons):
        if i % 2 == 1:
            result.append(row)
            row = [button.name, ]
        else:
            row.append(button.name)
    result.append(row)
    print(result)
    return result


def remove_filters(chat_id, text="Выберите категории, которые хотите удалить"):
    u = Users.query.filter_by(chat_id=chat_id).first()
    u.adding_filters = False
    db.session.commit()

    filters = u.filters
    if filters:
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


def add_user(chat_id, psw):
    psw_hash = generate_password_hash(psw)
    u = Users(chat_id=chat_id, psw=psw_hash, is_active=False, date=datetime.now())
    try:
        db.session.add(u)
        db.session.commit()
    except IntegrityError:
        pass


def get_users():
    return Users.query.all()
