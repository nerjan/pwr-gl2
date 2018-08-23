from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, \
                    SubmitField, RadioField, HiddenField, validators


class LoginForm(FlaskForm):
    '''Form that allows to login.'''
    username = StringField('Username')
    name = StringField('Name')
    surname = StringField('Last name')
    password = PasswordField('Password')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', [
        validators.Length(min=4, max=20,
                          message="Username has to be between 4 and 20 characters")
    ])
    name = StringField('Name', [
        validators.Length(min=4, max=20,
                      message="Name has to be between 4 and 20 characters")
    ])
    surname = StringField('Last name', [
        validators.Length(min=4, max=20,
                          message="Last name has to be between 4 and 20 characters")
    ])
    email = StringField('Email Address', [
        validators.Length(min=6, max=50,
                          message="Email has to be between 6 and 50 characters")
    ])
    password = PasswordField('Password', [
        validators.Required( message="You must provide a password."),
        validators.Length(min=5, max=50),
        validators.EqualTo('confirm', message='Passwords must match.')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField(
        'I accept the Terms of Service and Privacy Notice',
        [validators.Required(message="You have to accept this terms to use this site!")])
    submit = SubmitField('Register')


class QuestionareForm(FlaskForm):
    id = HiddenField("Question ID")
    show_all = BooleanField("Show answered questions too", default=True)
    answers = RadioField('Label')
    submit = SubmitField('Submit')
class ForgottenPasswordForm(FlaskForm):
    email = StringField('Email Address')
    submit = SubmitField('Remind password!')
    forgottenPassoword = SubmitField('I forget password')

