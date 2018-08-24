from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import yaml

handled_traits = ('agreeableness', 'conscientiousness', 'extraversion',
                  'neuroticism', 'openness')
db = SQLAlchemy()
login_manager = LoginManager()
