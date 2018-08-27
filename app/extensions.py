from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_caching import Cache
import yaml
from sqlalchemy import or_
handled_traits = ('agreeableness', 'conscientiousness', 'extraversion',
                  'neuroticism', 'openness')
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
cache = Cache()
