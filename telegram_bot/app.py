from flask import Flask, request
from .models import db, migrate
from .funcs import send_message, activate, deactivate
from backend.config import Configuration


app = Flask(__name__)
app.config.from_object(Configuration)

db.init_app(app)
migrate.init_app(app, db)


@app.route("/", methods=["GET", "POST"])
def receive_update():
    if request.method == "POST":
        print(request.json)
        chat_id = request.json["message"]["chat"]["id"]
        if request.json["message"]["text"] == "/activate":
            response = activate(chat_id)
            send_message(chat_id, response)
        elif request.json["message"]["text"] == "/deactivate":
            response = deactivate(chat_id)
            send_message(chat_id, response)

    return {"ok": True}
