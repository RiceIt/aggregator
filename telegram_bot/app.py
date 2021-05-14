import logging

from flask import Flask, request

from telegram_bot.models import db, migrate
from backend.config import Configuration
from telegram_bot.funcs import (start, activate, deactivate, add_filters, remove_filters, add_filter, adding_filter,
                                remove_filter, silent_mode_on, silent_mode_off, add_platforms, remove_platforms,
                                to_platforms, add_habr, remove_habr)


logging.basicConfig(level=logging.INFO, filename='logs.log', format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

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
            elif request.json["message"]["text"] in ("fl.ru", "freelance.ru"):
                platform = request.json["message"]["text"]
                if adding_filter(chat_id):
                    add_filters(chat_id, platform)
                else:
                    remove_filters(chat_id, platform)
            elif request.json["message"]["text"] == "freelance.habr.com":
                if adding_filter(chat_id):
                    add_habr(chat_id)
                else:
                    remove_habr(chat_id)
            else:
                category = request.json["message"]["text"]
                if adding_filter(chat_id):
                    add_filter(chat_id, category)
                else:
                    remove_filter(chat_id, category)
        except KeyError as e:
            logger.exception("KeyError occurred")

        except AttributeError as e:
            logger.exception("AttributeError occurred")

    return {"ok": True}
