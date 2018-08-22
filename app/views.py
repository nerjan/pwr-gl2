from flask import render_template, request, Blueprint
from flask import redirect, url_for, flash, session
from flask_menu import register_menu
import genomelink
import os
from flask_login import login_user, logout_user, current_user, login_required
from .extensions import db, login_manager
from .models import User, GLTrait, Question, Answer
from .forms import LoginForm, RegistrationForm, QuestionareForm, ForgottenPasswordForm
from .token import generate_confirmation_token, confirm_token
from .email import send_email
from strgen import StringGenerator
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

@main.route("/forgotten_password", methods=['GET', 'POST'])
def forgotten_password():
    forgottenForm = ForgottenPasswordForm()
    if forgottenForm.submit.data:
        email = forgottenForm.email.data
        #if email is in database then send remind password email
        user = db.session.query(User).filter_by(
                          email=email).first()
        if user:
            #generate random password
            password = StringGenerator('[\l\d]{4:18}&[\d]&[\p]').render()
            user.set_password(password)
            db.session.commit()
            html = render_template('remind.html', password=password, html = url_for('main.login', _external=True))
            send_email(email, "Pwr-gl2 reind password", html)
        flash("We send reminding email.")
        return redirect(url_for('main.index'))
    return render_template('forgotten_password.html', title='Remind passowrd', form=forgottenForm)

@main.route("/login", methods=['GET', 'POST'])
@register_menu(main, '.login', 'Sign in', order=4,
               visible_when=lambda: not current_user.is_authenticated)
def login():
    form = LoginForm()
    forgottenForm = ForgottenPasswordForm()
    if current_user.is_authenticated:
        flash("You are already logged in", 'warning')
        return redirect(url_for('main.index'))
    if forgottenForm.forgottenPassoword.data:
        return redirect(url_for('main.forgotten_password'))
    if form.validate_on_submit():
        # Check if username in database; get first first record only,
        # since username is unique
        user = db.session.query(User).filter_by(
                username=form.username.data).first()
        if user and user.check_password(form.password.data):
            # authentication successful, proceed to login
            if user.confirmed:
                flash('Logged in successfully as {}'.format(form.username.data),
                      'message')
                login_user(user, remember=form.remember_me.data)
                user.authenticated = True
                db.session.commit()
                return render_template('index.html')
            else:
                flash("You have to confirm your email!!")
                return render_template('index.html')
        else:
            flash("Wrong password or username", 'warning')
            return redirect(url_for('main.login'))
    return render_template('login.html', title='Sign In',
                           form=form, forgottenForm=forgottenForm)


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
    if not user:
        return

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
        'labels': [r['description'] for r in reports],
        'datasets': [
            {'label': 'Genomelink data',
             'data': [r['score'] for r in reports]}
        ]}

    return render_template('genome.html', reports=reports,
                           chart_data=chart_data,
                           authorize_url=authorize_url)


@main.route("/questionare", methods=['GET', 'POST'])
@login_required
@register_menu(main, '.questionare', 'Self-assessment questionare', order=2)
def questionare():
    '''Show self-assessment questionare'''

    form = QuestionareForm()
    if form.is_submitted():
        answer = Answer(question_id=form.id.data,
                        answer=int(form.answers.data)+1,
                        user_id=current_user.get_id())
        db.session.add(answer)
        db.session.commit()
        # Make sure that no answer is selected
        form.answers.data = -1
    if form.show_all:
        # Showing all questions in a circular fashion
        if form.id.data:
            next_id = int(form.id.data) + 1
            question = Question.query.get(next_id)
        else:
            question = Question.query.first()
        questions_left = Question.query.count()
    else:
        # Showing only unanswered quesitons, so take the next one
        my_answers = Answer.query.filter_by(author=current_user)
        answered_ids = [ ans.question_id for ans in my_answers ]
        questions_to_answer = Question.query.filter(~Question.id.in_(answered_ids))
        questions_left = questions_to_answer.count()
        question = questions_to_answer.first()
    if not questions_left:
        flash("Great, you have answered to all questions. Your answers were saved.")
        return render_template('index.html')

    answers = []
    for choice in range(len(question.choices)):
        answers.append((choice, question.choices[choice].value))
    form.answers.choices = answers
    data = {
        'question': question.value,
        'id': question.id,
        'count': questions_left}
    return render_template('questionare.html', data=data, form=form)


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
        name = form.name.data
        surname = form.surname.data
        email = form.email.data
        password = form.password.data
        #if there is no users with this username
        if db.session.query(User).filter_by(username=form.username.data).first():
            flash("The username is taken, please choose another one.",
                  "warning")
            return render_template('register.html', form=form)
        elif db.session.query(User).filter_by(email=form.email.data).first():
            flash("That email is already used.", "warning")
            return render_template('register.html', form=form)
        else:
            user = User(username=username, email=email, password=password, name=name, surname=surname)
            db.session.add(user)
            db.session.commit()
            flash("You registered succesfully!", "info")
            db.session.close()
            #create a confirmation link
            token = generate_confirmation_token(email)
            confirm_url = url_for('main.confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            #send confirmation email
            send_email(str(email), subject, html)

            return redirect(url_for('main.login'))
    else:
        flash_errors(form)
        return render_template("register.html", form=form)


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash("%s" % (error))


@main.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('main.index'))
@main.route("/userprofile", methods=['GET', 'POST'])
@login_required
@register_menu(main, '.userprofile', 'Your profile', order=7)
def userprofile():
    '''userprofile'''
    user_id = int(session['user_id'])
    user = db.session.query(User).filter(User.user_id == user_id).one()
    
    
    return render_template('userprofile.html', user=user)

