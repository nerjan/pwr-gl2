from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, \
                    SubmitField, RadioField, HiddenField, validators


class LoginForm(FlaskForm):
    '''Form that allows to login.'''
    username = StringField('Username')
    password = PasswordField('Password')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', [
        validators.Length(min=4, max=20,
                          message="Username has to be between 4 and 20 characters")
    ])
    email = StringField('Email Address', [
        validators.Length(min=6, max=50,
                          message="Email has to be between 6 and 50 characters")
    ])
    password = PasswordField('Password', [
        validators.Required(message="You must provide a password."),
        validators.EqualTo('confirm', message='Passwords must match.')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField(
        'I accept the Terms of Service and Privacy Notice',
        [validators.Required(message="You have to accept this terms to use this site!")])
    submit = SubmitField('Register')


class QuestionareForm(FlaskForm):
    id = HiddenField("Question ID")
    answers = RadioField('Label', default=0) #default value make sure that some answer will be chosen.
    submit = SubmitField('Submit')
