from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField


class LoginForm(FlaskForm):
    '''Form that allows to login. At the end of the project all forms could
    be in separated file'''
    username = StringField('Username')  #, validators=[DataRequired()])
                                        # I dont use it to make message "Wrong password or username" visible
    password = PasswordField('Password')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
