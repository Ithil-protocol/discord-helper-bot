# web.py
import os
from dotenv import load_dotenv
from flask import Flask
from flask import render_template
from tinydb import TinyDB, Query

load_dotenv()
DB_NAME = os.getenv('DB_NAME')

db = TinyDB(DB_NAME)
q = Query()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logs')
def logs():
    table = db.table('requests')
    req = table.all()
    return render_template('logs.html', len = len(req), requests = req)


@app.route('/errors')
def errors():
    table = db.table('errors')
    err = table.all()
    return render_template('errors.html', len = len(err), errors = err)

app.run()
