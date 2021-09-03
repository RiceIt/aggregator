from flask import Flask, request

from bot.config import Configuration
from bot.handlers import request_handler


app = Flask(__name__)
app.config.from_object(Configuration)


@app.route(f"/{Configuration.BOT_URI}", methods=["GET", "POST"])
def receive_update():
    request_handler(request.json)
    return {"ok": True}
