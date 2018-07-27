from flask import Flask
from flask_menu import Menu
import configparser
import os
from app.views import main


def prepare_env():
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read('config.ini')
    for key in config['global']:
        val = config['global'][key]
        os.environ[key] = val


app = Flask(__name__)
Menu(app=app)
prepare_env()
app.secret_key = os.urandom(24)
app.register_blueprint(main)
