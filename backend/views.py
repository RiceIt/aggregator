from flask import request, render_template

from backend.app import app
from backend.funcs import get_tasks
from backend.forms import CategoryForm
from telegram_bot.funcs import add_user, get_users


@app.route('/')
def task_list_view():
    context = {
        "tasks": get_tasks(),
        "users": get_users(),
        "form": CategoryForm(),
    }
    return render_template('index.html', **context)


@app.route('/register')
def register():
    add_user(78216412, 'saghf78wfygsh')
    context = {
        "tasks": get_tasks(),
        "form": CategoryForm(),
    }
    return render_template('index.html', **context)
