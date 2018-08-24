import configparser
import os

from flask import Flask
from flask_menu import Menu
from flask_migrate import Migrate
from flask_mail import Mail

from app.views import main
from app.extensions import db, login_manager, yaml
from app.models import Question_constructor, Choice_constructor, \
                       User, Question



app_dir = os.getcwd()

#path to users_pictures folder
UPLOAD_FOLDER = 'app/static/users_pictures'

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
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    Menu(app=app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "warning"
    return app


app = create_app()

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'pwrgl2confirm',
    "MAIL_PASSWORD": 'pwrgl2password',
    "SECRET_KEY": 'my_precious',
    "SECURITY_PASSWORD_SALT": 'my_precious_two',
    "MAIL_DEFAULT_SENDER": 'pwrgl2confirm@gmail.com'
}
app.config.update(mail_settings)


mail = Mail(app)
migrate = Migrate(app, db)

yaml.add_constructor('!question', Question_constructor)
yaml.add_constructor('!answer', Choice_constructor)