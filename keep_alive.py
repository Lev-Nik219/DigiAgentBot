# keep_alive.py
from flask import Flask, send_from_directory
from threading import Thread
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

# Чтобы не засорять логи, можно отдавать пустой ответ на запросы favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

def run():
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()