from flask import Flask
from flask_menu import Menu
from flask_migrate import Migrate
import configparser
import os
from app.views import main
from app.extensions import db, login_manager


app_dir = os.getcwd()


def prepare_env():
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read('config.ini')
    for key in config['global']:
        val = config['global'][key]
        os.environ[key] = val


class Config(object):

    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}/app.db'.format(app_dir)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app(config=Config):
    prepare_env()
    app = Flask(__name__)
    app.config.from_object(config)
    app.secret_key = os.urandom(24)
    app.register_blueprint(main)
    Menu(app=app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "warning"
    return app


app = create_app()
migrate = Migrate(app, db)
