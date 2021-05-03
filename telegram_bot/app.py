from flask import Flask, request
from .models import db, migrate
from .funcs import start, send_message, activate, deactivate, add_filters, remove_filters, add_filter, adding_filter, remove_filter, add_user
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
            if request.json["message"]["text"] == "/start" or request.json["message"]["text"] == "Назад":
                start(chat_id)
            elif request.json["message"]["text"] == "Активировать уведомления":
                response = activate(chat_id)
                send_message(chat_id, text=response)
            elif request.json["message"]["text"] == "Деактивировать":
                response = deactivate(chat_id)
                send_message(chat_id, text=response)
            elif request.json["message"]["text"] == "Добавить категории":
                add_filters(chat_id)
            elif request.json["message"]["text"] == "Удалить категории":
                remove_filters(chat_id)
            else:
                category = request.json["message"]["text"]
                if adding_filter(chat_id):
                    add_filter(chat_id, category)
                    # send_message(chat_id, response)
                else:
                    remove_filter(chat_id, category)
                    # send_message(chat_id, response)
        except KeyError:
            chat_id = request.json['my_chat_member']['chat']['id']
            print(chat_id)
            # add_user(chat_id, 'dasdasdas')

    return {"ok": True}
