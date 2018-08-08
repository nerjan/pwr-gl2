from flask import render_template, request, Blueprint
from flask import redirect, url_for, flash, session
from flask_menu import register_menu
import genomelink
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from flask_login import login_user, logout_user, LoginManager, current_user
from .extensions import db, login_manager
from .models import User
from functools import wraps

main = Blueprint('main', __name__)

traits = ('agreeableness', 'conscientiousness', 'extraversion', 'neuroticism',
          'openness')


@main.route("/")
@register_menu(main, '.home', 'Home', order=0)
def index():
    '''Display main view of the app'''
    return render_template('index.html')


class LoginForm(FlaskForm):
    '''Form that allows to login. At the end of the project all forms could
    be in separated file'''
    username = StringField('Username')  #, validators=[DataRequired()])
                                        # I dont use it to make message "Wrong password or username" visible
    password = PasswordField('Password')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@login_manager.user_loader
def load_user(id):
    '''This callback is used to reload the user object from the user ID
    stored in the session'''
    return db.session.query(User).get(int(id))


@main.route("/login", methods=['GET', 'POST'])
@register_menu(main, '.login', 'Sing in', order=4)
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        flash("You are already logged in")
        return redirect(url_for('index'))
    if form.validate_on_submit():
        '''check if username is in database- search to first username,
        because I assume there is no 2 users with the same username!!!'''
        user = db.session.query(User).filter_by(
                username=form.username.data).first()
        if user and form.password.data == user.password: #if username and password is ok login
            flash('Logged in successfully as {}'.format(form.username.data))
            login_user(user, remember=form.remember_me.data)
            return render_template('index.html')
        else:
            flash("Wrong password or username")
            return redirect(url_for('login'))
    return render_template('login.html', title='Sing In ',
                           form=form)


def login_required(f):
    '''is used to redirec if one want to get to page that should be allowed only for logged in user'''
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))

    return wrap


@main.route("/logout")
@login_required
@register_menu(main, '.logout', 'Sing out', order=5)
#HERE HOW TO DO TO SHOW ONLY SING IN OR SING OUT??!!
def logout():
    logout_user()
    return redirect(url_for('index'))


@main.route("/genome")
@login_required
@register_menu(main, '.genome', 'Genomic insight', order=1)
def genome():
    '''Display genomic insight based on GenomeLink API'''

    scope = ['report:{}'.format(t) for t in traits]
    authorize_url = genomelink.OAuth.authorize_url(scope=scope)

    reports = []
    if session.get('oauth_token'):
        for name in traits:
            reports.append(genomelink.Report.fetch(
                                name=name,
                                population='european',
                                token=session['oauth_token']))

    return render_template('genome.html', reports=reports,
                           authorize_url=authorize_url)


@main.route("/questionare")
@login_required
@register_menu(main, '.questionare', 'Self-assessment questionare', order=2)
def questionare():
    '''Show self-assessment questionare'''
    return render_template('index.html')


@main.route("/selfassessment")
@login_required
@register_menu(main, '.selfassessment', 'Self-assessment results', order=3)
def selfassessment():
    '''Show self-assessment results'''
    return render_template('index.html')


@main.route("/callback")
def callback():

    try:
        token = genomelink.OAuth.token(request_url=request.url)

    except genomelink.errors.GenomeLinkError as e:
        flash('Authorization failed.')
        if os.environ.get('DEBUG') == '1':
            flash('[DEBUG] ({}) {}'.format(e.error, e.description))
        return redirect(url_for('genome'))

    session['oauth_token'] = token
    return redirect(url_for('main.genome'))
