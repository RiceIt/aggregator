from flask import Flask, render_template

from backend.config import Configuration


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


app.config.from_object(Configuration)
app.run()
