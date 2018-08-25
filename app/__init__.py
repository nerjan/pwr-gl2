import configparser
import os
from os import path

from flask import Flask
from flask_menu import Menu
from flask_migrate import Migrate

from app.views import main
from app.extensions import db, login_manager, yaml, mail
from app.models import Question_constructor, Choice_constructor, \
                       User, Question


app_dir = path.abspath(__file__)
app_dir = path.dirname(app_dir)
app_dir = path.split(app_dir)[0]

class MetaConfig(type):

    def __init__(cls, name, bases, dct):
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read('config.ini')
        for section in config.sections():
            for key in config[section]:
                val = config[section][key]
                setattr(cls, key, val)
                if section == 'genomelink':
                    os.environ[key] = val


class Config(metaclass=MetaConfig):

    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}/app.db'.format(app_dir)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.secret_key = os.urandom(24)
    app.register_blueprint(main)
    Menu(app=app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "warning"
    mail.init_app(app)
    return app


app = create_app()

migrate = Migrate(app, db)

yaml.add_constructor('!question', Question_constructor)
yaml.add_constructor('!answer', Choice_constructor)
