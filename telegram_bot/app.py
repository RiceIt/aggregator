from flask import Flask, request

from models import db, migrate
from funcs import (start, activate, deactivate, add_filters, remove_filters, add_filter, adding_filter,
                    remove_filter, silent_mode_on, silent_mode_off, add_platforms, remove_platforms, to_platforms)
from backend.config import Configuration


app = Flask(__name__)
app.config.from_object(Configuration)

db.init_app(app)
migrate.init_app(app, db)


@app.route("/", methods=["GET", "POST"])
def receive_update():
    if request.method == "POST":
        print(request.json)
        try:
            chat_id = request.json["message"]["chat"]["id"]
            if request.json["message"]["text"] == "/start" or request.json["message"]["text"] == "Вернуться":
                start(chat_id)
            elif request.json["message"]["text"] == "Включить уведомления":
                activate(chat_id)
            elif request.json["message"]["text"] == "Отключить уведомления":
                deactivate(chat_id)
            elif request.json["message"]["text"] == "Включить беззвучный режим":
                silent_mode_on(chat_id)
            elif request.json["message"]["text"] == "Отключить беззвучный режим":
                silent_mode_off(chat_id)
            elif request.json["message"]["text"] == "Добавить категории":
                add_platforms(chat_id)
            elif request.json["message"]["text"] == "Удалить категории":
                remove_platforms(chat_id)
            elif request.json["message"]["text"] == "<< К платформам":
                to_platforms(chat_id)
            elif request.json["message"]["text"] == "fl.ru":
                if adding_filter(chat_id):
                    add_filters(chat_id)
                else:
                    remove_filters(chat_id)
            else:
                category = request.json["message"]["text"]
                if adding_filter(chat_id):
                    add_filter(chat_id, category)
                else:
                    remove_filter(chat_id, category)
        except KeyError:
            print(request.json)
            pass

    return {"ok": True}
