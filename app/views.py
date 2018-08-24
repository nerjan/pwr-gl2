from flask import render_template, request, Blueprint
from flask import redirect, url_for, flash, session
from flask_menu import register_menu
import genomelink
import os
from flask_login import login_user, logout_user, current_user, login_required
from .extensions import db, login_manager, handled_traits
from .models import User, Question, Answer, SelfAssesmentTraits, Choice
from .forms import LoginForm, RegistrationForm, QuestionareForm, ForgottenPasswordForm, SelfAssesmentBarsForm, ChooseTraitTestForm
from .token import generate_confirmation_token, confirm_token
from .email import send_email
from random import randint
from strgen import StringGenerator
from .helper import flash_errors, genome, selfassesmenttraitsresults, mean_user_scores, mean_user_scores_percentage
import app


main = Blueprint('main', __name__)

@main.route("/")
@register_menu(main, '.home', 'Home', order=0)
def index():
    #some quotes to make it more interesting
    f=open("app/templates/quotes.txt")
    lines = f.readlines()
    '''Display main view of the app'''
    return render_template('index.html', quote=lines[randint(0, len(lines)-1)])

@main.route("/choose_trait_test", methods=['GET', 'POST'])
@login_required
@register_menu(main, '.choose_trait_test', 'Personality test', order=1,
               visible_when=lambda: current_user.is_authenticated)
def choose_trait_test():
    colors = ["#e95095", "#ffcc00", "orange", "deepskyblue", "green"]
    b_colors = ["#e95095", "#ffcc00", "orange", "deepskyblue", "green"]
    form = ChooseTraitTestForm()
    if form.is_submitted():
        return redirect(url_for("main.questionare", trait=request.form['submit']))
    return render_template("choose_trait_test.html", handled_traits=handled_traits, form=form, colors=colors[::-1], b_colors=b_colors[::-1])


@main.route("/questionare", methods=['GET', 'POST'])
@login_required
# @register_menu(main, '.questionare', 'Personality test', order=1)
def questionare():
    '''Show self-assessment questionare'''
    # next_id = 0
    trait = request.args['trait']        #take trait from choose_trait_test button that was clicked
    form = QuestionareForm()
    #adding answet to db
    if form.is_submitted():
        #If in db is answer for this question update it in not just add.
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

    trait_questions = db.session.query(Question).filter_by(trait=trait) #list of db records of questions from THIS TRAIT only
    '''WHEN ALL TRAITS WILL BE AVAILABLE WE CAN DELETE THIS'''
    if not trait_questions.count():
        flash("There is no question for this trait", "info")
        return redirect(url_for('main.index'))

    number_of_questions = trait_questions.count() #idk if it is important
    first_id = trait_questions.first().id #id of 1st question in this trait, start from here

    if form.show_all.data: #if checkbox is checked (default) - answer to all questions
        # Showing all questions in a circular fashion
        if form.id.data:
            next_id = 1 + int(form.id.data)
            question =Question.query.get(next_id)
            form.id.data = next_id
        else: #if this is 1st question
            next_id = first_id
            form.id.data = next_id
            question = Question.query.get(first_id)
        try:# if there is no more questions in trait_questions, finish
            x= trait_questions.filter_by(id=next_id).first().id
        except AttributeError:
            return redirect(url_for("main.index"))
    else:
        # Showing only unanswered quesitons, so take the next one
        my_answers = Answer.query.filter_by(author=current_user)
        answered_ids=[]
        if answered_ids==[]:
            for ans in my_answers:
                if db.session.query(Question).filter_by(id=ans.question_id).first().trait == trait:
                    answered_ids.append(ans.question_id) #list of question ids which was ansered for this trait
        '''if error do this:'''
        #if answered_ids ==[]:
            # return redirect(url_for("main.index"))

        # answered_ids = [ans.question_id for ans in my_answers]                      #list of question ids which was ansered
        questions_to_answer = Question.query.filter(~Question.id.in_(answered_ids)).filter_by(trait=trait)   #search all non answered questions for this traid
        question = questions_to_answer.first()
        if not question:
            flash("You already answered to all questions")
            return redirect(url_for("main.index"))

    answers = []
    for choice in range(len(question.choices)):
        answers.append((choice, question.choices[choice].value))
    form.answers.choices = answers
    data = {
        'question': question.value,
        'id': question.id,
        'count': number_of_questions}
    return render_template('questionare.html', data=data, form=form)

x=0
ans=[0 for x in handled_traits]
@main.route("/selfassessmenttraits", methods=['GET', 'POST'])
@login_required
@register_menu(main, '.selfassessmenttraits', 'Self-assessment', order=2,
               visible_when=lambda: current_user.is_authenticated)
def selfassessmenttraits():
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
@register_menu(main, '.selfassessmenttest', 'Personality test results', order=3,
               visible_when=lambda: current_user.is_authenticated)
def selfassessment_testresult():
    '''Show self-assessment results'''
    text="What your personality test tells about you."
    return render_template('sab.html', answers=mean_user_scores_percentage(), trait=handled_traits, text=text)




@main.route("/selfassesmentresult", methods=['GET', 'POST'])
@login_required
@register_menu(main, '.selfassessmentresults', 'Self-assessment results', order=4,
               visible_when=lambda: current_user.is_authenticated)
def selfassesmentresults():
    '''Shows result for self-assesment, NOT for test'''
    text="How do you think about yourself."
    return render_template('sab.html', answers=selfassesmenttraitsresults(), trait=handled_traits, text=text)



@main.route("/results")
@login_required
@register_menu(main, '.results', 'Results', order=5,
               visible_when=lambda: current_user.is_authenticated)
def results_radar():                                        #mozna dodac ze jesli genome puste to zapelnij czyms
    '''Take all results and store it in radar.
    I use previous script and didnt hange it,
    so thats why there is chart_datas in this way'''
    genome_results = genome()
    chart_data_test = {
        'labels': [r for r in handled_traits],
        'datasets': [
            {'label': 'Personal test',
             'data':  mean_user_scores()}
                 ]}
    selfassesment =[int(x*5/100) for x in selfassesmenttraitsresults()] #this *5/100 is complicated... but it works...
    chart_data_self={
        'labels': [r for r in handled_traits],
        'datasets': [
            {'label': 'Self-assesment',
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
    return redirect(url_for('main.results_radar'))

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


@main.route('/register/', methods=["GET", "POST"])
@register_menu(main, '.register', 'Registration', order=22,
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
@register_menu(main, '.userprofile', 'Your profile', order=7,
               visible_when=lambda: current_user.is_authenticated)
def userprofile():
    '''userprofile'''
    return render_template('userprofile.html', user=current_user)



@login_required
@main.route('/upload_image', methods=['GET', 'POST'])
def upload_file():
    try:                                #go 1st to this upload, then do the rest of the code
        file=request.files['image']
    except KeyError:
        return render_template("upload_image.html")
    flash(app.app.config['UPLOAD_FOLDER'])
    file.filename = current_user.username+".jpg"    #rename to username.jpg -important for the rest functions
    f = os.path.join(app.app.config['UPLOAD_FOLDER'], file.filename)

    # add your custom code to check that the uploaded file is a valid image and not a malicious file (out-of-scope for this post)
    file.save(f)
    return render_template('index.html')