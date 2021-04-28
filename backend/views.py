from flask import render_template

from backend.app import app
from backend.funcs import get_tasks, add_user, get_users


@app.route('/')
def task_list_view():
    context = {
        "tasks": get_tasks(),
        "users": get_users()
    }
    return render_template('index.html', **context)


@app.route('/add_user')
def add_user_view():
    add_user()
    return render_template('index.html')
