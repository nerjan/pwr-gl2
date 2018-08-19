from flask import render_template, request, Blueprint
from flask import redirect, url_for, flash, session
from flask_menu import register_menu
import genomelink
import os
from flask_login import login_user, logout_user, current_user, login_required
from .extensions import db, login_manager
from .models import User, GLTrait, Question, Answer
from .forms import LoginForm, RegistrationForm, QuestionareForm


main = Blueprint('main', __name__)

handled_traits = ('agreeableness', 'conscientiousness', 'extraversion',
                  'neuroticism', 'openness')


@main.route("/")
@register_menu(main, '.home', 'Home', order=0)
def index():
    '''Display main view of the app'''
    return render_template('index.html')


@login_manager.user_loader
def load_user(id):
    '''This callback is used to reload the user object from the user ID
    stored in the session'''
    return db.session.query(User).get(int(id))


@main.route("/login", methods=['GET', 'POST'])
@register_menu(main, '.login', 'Sing in', order=4,
               visible_when=lambda: not current_user.is_authenticated)
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        flash("You are already logged in", 'warning')
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        # Check if username in database; get first first record only,
        # since username is unique
        user = db.session.query(User).filter_by(
                username=form.username.data).first()
        if user and user.check_password(form.password.data):
            # authentication successful, proceed to login
            flash('Logged in successfully as {}'.format(form.username.data),
                  'message')
            login_user(user, remember=form.remember_me.data)
            user.authenticated = True
            db.session.commit()
            return render_template('index.html')
        else:
            flash("Wrong password or username", 'warning')
            return redirect(url_for('main.login'))
    return render_template('login.html', title='Sing In ',
                           form=form)


@main.route("/logout")
@login_required
@register_menu(main, '.logout', 'Sign out', order=5,
               visible_when=lambda: current_user.is_authenticated)
def logout():
    logout_user()
    current_user.authenticated = False
    db.session.commit()
    return redirect(url_for('main.index'))


@main.route("/genome")
@login_required
@register_menu(main, '.genome', 'Genomic insight', order=1)
def genome():
    '''Display genomic insight based on GenomeLink API'''

    scope = ['report:{}'.format(t) for t in handled_traits]
    authorize_url = genomelink.OAuth.authorize_url(scope=scope)

    user_id = int(session['user_id'])
    user = User.query.filter_by(id=user_id).first()
    if not user: return

    # Retrieve reports for current user from the DB
    report_objects = {}
    db_traits = GLTrait.query.filter_by(user=user)
    for name in handled_traits:
        record = db_traits.filter_by(trait=name).first()
        if record:
            report_objects[name] = record

    if session.get('gl_oauth_token'):

        # Reports were fetched from Genomelink API
        for name in handled_traits:
            fetched = genomelink.Report.fetch(
                                name=name,
                                population='european',
                                token=session['gl_oauth_token'])
            description = fetched.phenotype['display_name']
            score = fetched.summary['score']

            if name in report_objects:
                # Replace record if exists
                report_objects[name].description = description
                report_objects[name].t_score = score
            else:
                # No such record, then add to the DB
                tr = GLTrait(trait=name,
                         description=description,
                         t_score=score,
                         user=user)
                report_objects[name] = tr
                db.session.add(tr)
        db.session.commit()

        # Clear token, so that refresh is skipped on reload
        session.pop('gl_oauth_token', None)

    reports = []
    for name in handled_traits:
        if name in report_objects:
            reports.append(report_objects[name].serialize())

    chart_data = {
        'labels': [ r['description'] for r in reports ],
        'datasets': [
            { 'label': 'Genomelink data',
              'data' : [ r['score'] for r in reports ],
            }
        ]}

    return render_template('genome.html', reports=reports,
                           chart_data=chart_data,
                           authorize_url=authorize_url)

#not the best way
questionNumber=1 # 1 because first if form.is_submitted() below is not executed(there wasnt submit yet
@main.route("/questionare", methods=['GET', 'POST'])
@login_required
@register_menu(main, '.questionare', 'Self-assessment questionare', order=2)
def questionare():
    '''Show self-assessment questionare'''
    global questionNumber
    length = Question.query.count() #how many questions
    if questionNumber<length:
        form =QuestionareForm()
        if form.is_submitted():
            questionNumber+=1
        question = Question.query.filter_by(id=questionNumber).first() #take a question

        # put answers to question in form.answers
        answers=[]
        for choice in range(len(question.choices)):
            answers.append((choice, question.choices[choice].value))
        form.answers.choices=answers

        db.session.add(Answer(question_id=questionNumber, answer=int(form.answers.data)+1, user_id=current_user.get_id()))
        db.session.commit()
        return render_template('questionare.html', data=question, form=form, questionNumber=questionNumber)
    questionNumber = 1 #reset
    flash("Great, you answer on every questions. Your answers are saved.")
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
        flash('Authorization failed.', 'warning')
        if os.environ.get('DEBUG') == '1':
            flash('({}) {}'.format(e.error, e.description), 'info')
        return redirect(url_for('main.genome'))

    session['gl_oauth_token'] = token
    return redirect(url_for('main.genome'))


@main.route('/register/', methods=["GET", "POST"])
@register_menu(main, '.register', 'Registration', order=6,
               visible_when=lambda: not current_user.is_authenticated)
def register():
    form = RegistrationForm(request.form)

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        #if there is no users with this username
        if db.session.query(User).filter_by(username=form.username.data).first():
            flash("The username is taken, please choose another one.")
            return render_template('register.html', form=form)
        elif db.session.query(User).filter_by(email=form.email.data).first():
            flash("That email is already used.")
            return render_template('register.html', form=form)
        else:
            db.session.add(User(username=username, email=email, password=password))
            db.session.commit()
            flash("You registered succesfully!")
            db.session.close()
            return redirect(url_for('main.login'))
    else:
        flash_errors(form)
        return render_template("register.html", form=form)


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash("%s" % (error))