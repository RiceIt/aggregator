from datetime import datetime

from werkzeug.security import generate_password_hash

from telegram_bot.models import db, Users
import requests


def send_message(chat_id, text):
    method = "sendMessage"
    token = "1383053016:AAGpBAnQ6KyDwiQj0HVIyMpRuUwk2Pww9cU"
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


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


def add_user(chat_id, psw):
    psw_hash = generate_password_hash(psw)
    u = Users(chat_id=chat_id, psw=psw_hash, date=datetime.now())
    db.session.add(u)
    db.session.commit()
