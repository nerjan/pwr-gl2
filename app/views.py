from flask import render_template, request, Blueprint
from flask import redirect, url_for, flash, session
from flask_menu import register_menu
import genomelink
import os
from flask_login import login_user, logout_user, current_user, login_required
from .extensions import db, login_manager
from .models import User, GLTrait, Question, Answer, \
                    Friends, SelfAssesmentTraits, Choice
from .forms import LoginForm, RegistrationForm, QuestionareForm, \
                   ForgottenPasswordForm, SelfAssesmentBarsForm, \
                   SearchForm, FriendRequest
from .token import generate_confirmation_token, confirm_token
from .email import send_email
from random import randint
from strgen import StringGenerator
from sqlalchemy import or_, and_


main = Blueprint('main', __name__)


handled_traits = ('agreeableness', 'conscientiousness', 'extraversion',
                  'neuroticism', 'openness')
@main.route("/")
@register_menu(main, '.home', 'Home', order=0)
def index():
    #some quotes to make it more interesting
    f=open("app/templates/quotes.txt")
    lines = f.readlines()

    '''Display main view of the app'''
    return render_template('index.html', quote=lines[randint(0, len(lines)-1)])


@login_manager.user_loader
def load_user(id):
    '''This callback is used to reload the user object from the user ID
    stored in the session'''
    return db.session.query(User).get(int(id))


@main.route("/questionare", methods=['GET', 'POST'])
@login_required
@register_menu(main, '.questionare', 'Personality test', order=1,
               visible_when=lambda: current_user.is_authenticated)
def questionare():
    '''Show self-assessment questionare'''
    form = QuestionareForm()
    if form.is_submitted():
        anser_in_database =db.session.query(Answer).filter_by(user_id=current_user.id, question_id=form.id.data).first()
        if anser_in_database:
            anser_in_database.answer=int(form.answers.data) + 1
            anser_in_database.score=db.session.query(Choice).filter_by(trait_id=form.id.data)[int(form.answers.data)].score
        else:
            answer = Answer(question_id=form.id.data,
                            answer=int(form.answers.data) + 1,
                            user_id=current_user.get_id(),
                            score=db.session.query(Choice).filter_by(trait_id=form.id.data)[int(form.answers.data)].score)   #take choices to question of id =form.id.data and from there only particular choice and score of this choice
            db.session.add(answer)
        db.session.commit()
        # Make sure that no answer is selected
        # form.answers.data = -1 #if we want to have no error, better be selected something
    if form.show_all.data: #there was form.show_all which basicly means nothing for "if"
        # Showing all questions in a circular fashion
        if form.id.data:
            next_id = int(form.id.data) + 1
            question = Question.query.get(next_id)
        else:
            question = Question.query.first()
        questions_left = 10 # It just has to be
        try:
            questions_left = Question.query.count() - int(form.id.data)   # it wasnt changing, it was always "17" so it didnt count
        except TypeError:
            pass
    else:
        # Showing only unanswered quesitons, so take the next one
        my_answers = Answer.query.filter_by(author=current_user)
        answered_ids = [ans.question_id for ans in my_answers]                      #list of question ids which was ansered
        questions_to_answer = Question.query.filter(~Question.id.in_(answered_ids))
        questions_left = questions_to_answer.count()
        question = questions_to_answer.first()
    if not questions_left:
        flash("Great, you have answered to all questions. Your answers were saved.")
        return redirect(url_for('main.index'))

    answers = []
    for choice in range(len(question.choices)):
        answers.append((choice, question.choices[choice].value))
    form.answers.choices = answers
    data = {
        'question': question.value,
        'id': question.id,
        'count': Question.query.count()}
    return render_template('questionare.html', data=data, form=form)


x=0
ans=[0 for x in handled_traits]
@main.route("/selfassessmenttraits", methods=['GET', 'POST'])
@login_required
@register_menu(main, '.selfassessmenttraits', 'Self-assessment traits', order=2)
def selfassessmenttraits():
    global handled_traits
    #this 2 global are bad, but it is working, so lets left it here
    global x
    global ans
    traits = handled_traits #take trait tuple
    form= SelfAssesmentBarsForm()
    #if user dont answer to all traits
    if x < len(traits):
        trait = traits[x]
        # if form.validate_on_submit():
        if form.is_submitted():
            ans[x]=int(form.answers.data)*20 #to make it from 20% to 100%
            x+=1
            # take next trait
        try:
            trait = traits[x]   #at the end, the index will be out of handled_traits tuple, so. Here it is neccessary to noc answer first question 2 times at the beggining.
            return render_template('selfassesmentbar.html', form=form, trait=trait) # go next trait quiz
        except IndexError:
            pass
    user_traits= db.session.query(SelfAssesmentTraits).filter_by(user_id=current_user.id).first()
    if user_traits: #if user already answered to questions change his answer to new one
        user_traits.agreeableness=ans[0]
        user_traits.conscientiousness=ans[1]
        user_traits.extraversion =ans[2]
        user_traits.neuroticism=ans[3]
        user_traits.openness=ans[4]
    else: #if not, add him to database
        sat= SelfAssesmentTraits(agreeableness=ans[0], conscientiousness=ans[1], extraversion =ans[2],
                                 neuroticism=ans[3], openness=ans[4], user_id =current_user.id)
        db.session.add(sat)
    db.session.commit()
    x=0
    return redirect(url_for('main.selfassesmentresults'))

@main.route("/selfassessmenttest")
@login_required
@register_menu(main, '.selfassessmenttest', 'Personality test results', order=3)
def selfassessmenttestresult():
    '''Show self-assessment results'''
    text="What your personality test shows you are."
    return render_template('sab.html', answers=mean_user_scores_percentage(), trait=handled_traits, text=text)

def mean_user_score(trait):
    '''Calculate user score for particular trait
    and then make mean value with respect to max_trait_score'''
    score =0
    user_answers=db.session.query(Answer).filter_by(user_id=current_user.id)                            #all user answers (with question_id and score for HIS answer)
    for answer in user_answers:                                                                         #take 1 answer
        question=db.session.query(Question).filter_by(id=answer.question_id).first()
        if question.trait == trait:
            question_weight = question.weight                                                           # weight of question that $answer is answer
            answer_score = answer.score                                                                 # How "good" is his answer, how many score has
            score += question_weight*answer_score                                                           # add real value of answer to score
    try:
        return int(score / max_trait_score(trait) * 100)  # in percentage
    except ZeroDivisionError:
        return 0 # if user didnt answer to any question then 0 to make it possible to show results without error


def max_trait_score(trait):
    '''Calculate max possible score from test questions for trait'''
    all_questions = db.session.query(Question).filter_by(trait=trait)                                      #take all questions
    score=0
    for question in all_questions:
        quest= db.session.query(Choice).filter_by(trait_id=question.id)                    #take one of them
        max_score = max(x.score for x in quest) # take the biggest value of available choice score   #MAKE MAX FROM ALL
        weight = question.weight                                                    #take question weight
        score += max_score*weight                                                   #add to max_score
    return score                                                                    #return one trait max score

def mean_user_scores_percentage():
    return [mean_user_score(x) for x in handled_traits] #in percentage

def mean_user_scores():
    return [int(x/100*5) for x in mean_user_scores_percentage()]                                             #for 5 step scale !!!!!!!!!

@main.route("/selfassesmentresult", methods=['GET', 'POST'])
@login_required
@register_menu(main, '.selfassessmentresults', 'Self-assessment results', order=4)
def selfassesmentresults():
    '''Shows result for self-assesment, NOT for test'''
    text="How do you think about yourself."
    return render_template('sab.html', answers=selfassesmenttraitsresults(), trait=handled_traits, text=text)

# @main.route("/selfassesmenttraitsresults", methods=['GET', 'POST'])
# @login_required
# @register_menu(main, '.selfassessmentbarsresults', 'Self-assessment-bars results', order=8)
def selfassesmenttraitsresults():
    '''take users answers for sels-assesment, NOT for test.
    It will be used in selfassesmentresults abowe'''
    user_traits= db.session.query(SelfAssesmentTraits).filter_by(user_id=current_user.id).first()
    answers=[0, 0, 0, 0, 0] #to make sure there are some answers
    # if not user_traits:
        # flash("There is no results yet! Make an assesment.", "info")
        # return redirect(url_for('main.selfassessmenttraits'))
    if user_traits:
        answers[0]= user_traits.agreeableness
        answers[1] =user_traits.conscientiousness
        answers[2] =user_traits.extraversion
        answers[3] =user_traits.neuroticism
        answers[4] =user_traits.openness
    return answers

@main.route("/results")
@login_required
@register_menu(main, '.results', 'Results', order=5)
def results_radar():                                        #mozna dodac ze jesli genome puste to zapelnij czyms
    '''Take all results and store it in radar.
    I use previous script and didnt hange it,
    so thats why there is chart_datas in this way'''
    genome_results = genome()
    chart_data_test = {
        'labels': [r for r in handled_traits],
        'datasets': [
            {'label': 'Personal test results',
             'data':  mean_user_scores()}
                 ]}
    selfassesment =[int(x*5/100) for x in selfassesmenttraitsresults()] #this *5/100 is complicated... but it works...
    chart_data_self={
        'labels': [r for r in handled_traits],
        'datasets': [
            {'label': 'Personal assesment',
             'data': selfassesment }
                 ]}
    how_hany_trais = len(handled_traits)
    return render_template('genome.html',
                           chart_data_test=chart_data_test,
                           chart_data_genome = genome_results[1],
                           chart_data_self = chart_data_self,
                           reports = genome_results[0],
                           authorize_url=genome_results[2],
                           test_restul= mean_user_scores(),
                           selfassesment=selfassesment,
                           how_hany_trais=how_hany_trais)

# @main.route("/genome")
# @login_required
# @register_menu(main, '.genome', 'Genomic insight', order=1)
def genome():
    '''Based on GenomeLink API take all neeccessary data to
    pass it to result_radar function'''
    #probably some problems with logging in but idk, its hard to check
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
    return (reports, chart_data, authorize_url)
    # return render_template('genome.html', reports=reports,
    #                        chart_data=chart_data,
    #                        authorize_url=authorize_url)

@main.route("/callback")
def callback():

    try:
        token = genomelink.OAuth.token(request_url=request.url)

    except genomelink.errors.GenomeLinkError as e:
        flash('Authorization failed.', 'warning')
        if os.environ.get('DEBUG') == '1':
            flash('({}) {}'.format(e.error, e.description), 'info')
        return redirect(url_for('main.index'))

    session['gl_oauth_token'] = token
    return redirect(url_for('main.genome'))


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
@register_menu(main, '.login', 'Sign in', order=20,
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
@register_menu(main, '.logout', 'Sign out', order=21,
               visible_when=lambda: current_user.is_authenticated)
def logout():
    logout_user()
    current_user.authenticated = False
    db.session.commit()
    return redirect(url_for('main.index'))


@main.route('/register', methods=["GET", "POST"])
@register_menu(main, '.register', 'Registration', order=22,
               visible_when=lambda: not current_user.is_authenticated)
def register():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        username = form.username.data
        name = form.name.data.title()
        surname = form.surname.data.title()
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
@register_menu(main, '.userprofile', 'Your profile', order = 7,
               visible_when = lambda: current_user.is_authenticated)
def userprofile():
    '''userprofile'''
    form = SearchForm(request.form)
    #Search friend on submit
    if form.validate_on_submit():
        searchfriend = form.searchfriend.data.split(' ')
        if len(searchfriend) == 0:
            flash('You have to write name or/and surname', 'warning')
        elif len(searchfriend) == 1:
            messages = searchfriend[0] + ' 0'
        else:
            messages = searchfriend[0] + ' ' + searchfriend[1]
        session['messages'] = messages
        return redirect(url_for('main.search', messages = messages))
        #fsearch = search(db.session.query(User), searchfriend)
    #current user name and surname
    user = db.session.query(User).filter_by(
                          id=current_user.id).first()
    #looking for friend IDs
    idfriends = db.session.query(Friends).with_entities(Friends.friend_id).filter_by(user_id=current_user.id).all()
    #Looking fo friends, addin no friends if possible
    friends=[db.session.query(User).filter_by(
                          id=friend.friend_id).first() for friend in idfriends]
    return render_template('userprofile.html', user = user, form = form)

@main.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    '''searchresults'''
    user_id = current_user.id
    form = FriendRequest()
    messages = session['messages'].split(' ')
    results = User.query.with_entities(User.surname, User.name, User.id).filter(or_(
                                       User.name == messages[0].strip().lower().title(), 
                                       User.surname == messages[1].strip().lower().title())).all()
    #Adding friends to DB
    if form.is_submitted():
        friend_id = request.form['submit']
        is_friend = db.session.query(Friends).filter(Friends.user_id == user_id,
                                                 Friends.friend_id == friend_id)
        flash('Adding friend')
        #Does not work properly
        if user_id == friend_id:
            flash('You can not add yourself')
        elif is_friend:
            flash('You are friends already')
        else:
            flash('You added new friend')
            connection = Friend(user_id=user_id,
                                      friend_id=friend_id,
                                          status="Requested")
            db.session.add(connection)
            db.session.commit()
    return render_template('search.html', results = results, form = form, user_id = user_id)
