from flask import render_template

from backend.app import app
from backend.funcs import get_tasks
from backend.forms import CategoryForm
from telegram_bot.funcs import get_users


@app.route('/')
def task_list_view():
    context = {
        "tasks": get_tasks(),
        "users": get_users(),
        "form": CategoryForm(),
    }
    return render_template('index.html', **context)
