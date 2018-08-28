from flask import render_template, request, Blueprint
from flask import redirect, url_for, flash, session
from flask_menu import register_menu
import genomelink
import os
from flask_login import login_user, logout_user, current_user, login_required
from .extensions import db, login_manager, handled_traits, cache
from .models import User, Question, Answer, SelfAssesmentTraits, \
                    Choice, Friends, FriendAssesment, FriendAnswer
from .forms import LoginForm, RegistrationForm, QuestionareForm, \
                   ForgottenPasswordForm, SelfAssesmentBarsForm, \
                   ChooseTraitTestForm, SearchForm, FriendRequest
from .token import generate_confirmation_token, confirm_token
from .email import send_email
from random import randint
from strgen import StringGenerator
from .helper import flash_errors, genome, selfassesmenttraitsresults, \
                    mean_user_scores, mean_user_scores_percentage, \
                    friend_assesment_result, make_filter, friend_mean_user_scores, \
                    friend_mean_user_scores_percentage, friend_answer_from_one,\
                    user_answer_for_friend
from sqlalchemy import or_
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
        return redirect(url_for('main.choose_trait_test'))

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
            return redirect(url_for("main.choose_trait_test"))
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
            return redirect(url_for("main.choose_trait_test"))

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
            return render_template('selfassesmentbar.html', form=form, trait=trait, user=current_user, visible=False) # go next trait quiz
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
    return redirect(url_for('main.results_bars'))

# @main.route("/selfassessmenttest")
# @login_required
# @register_menu(main, '.selfassessmenttest', 'Personality test results', order=3,
#                visible_when=lambda: current_user.is_authenticated)
# def selfassessment_testresult():
#     '''Show self-assessment results'''
#     text="What your personality test tells about you."
#     return render_template('sab.html', answers=mean_user_scores_percentage(), trait=handled_traits, text=text)
#
#
#
#
# @main.route("/selfassesmentresult", methods=['GET', 'POST'])
# @login_required
# @register_menu(main, '.selfassessmentresults', 'Self-assessment results', order=4,
#                visible_when=lambda: current_user.is_authenticated)
# def selfassesmentresults():
#     '''Shows result for self-assesment, NOT for test'''
#     text="How do you think about yourself."
#     return render_template('sab.html', answers=selfassesmenttraitsresults(), trait=handled_traits, text=text)
#
# @main.route("/friendassesmentresult", methods=['GET', 'POST'])
# @login_required
# @register_menu(main, '.friendassessmentresults', 'Friend-assessment results', order=14,
#                visible_when=lambda: current_user.is_authenticated)
# def friendassesmentresults():
#     '''Shows result for self-assesment, NOT for test'''
#     text="How other thinks about yourself."
#     return render_template('sab.html', answers=friend_assesment_result(), trait=handled_traits, text=text)

@main.route("/results")
@login_required
@register_menu(main, '.results', 'Results', order=5,
               visible_when=lambda: current_user.is_authenticated)
def results_radar():                                        #mozna dodac ze jesli genome puste to zapelnij czyms
    '''Take all results and store it in radar.
    I use previous script and didnt hange it,
    so thats why there is chart_datas in this way'''
    genome_results = genome()
    #charts are used to make radar rest is to make table
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
    friendassesment = friend_mean_user_scores()
    chart_data_friends={
        'labels': [r for r in handled_traits],
        'datasets': [
            {'label': 'Friend-assesment',
             'data': friendassesment}
                 ]}
    how_hany_trais = len(handled_traits)
    return render_template('genome.html',
                           chart_data_test=chart_data_test,
                           chart_data_genome = genome_results[1],
                           chart_data_self = chart_data_self,
                           chart_data_friends=chart_data_friends,
                           friendassesment=friendassesment,
                           reports = genome_results[0],
                           authorize_url=genome_results[2],
                           test_restul= mean_user_scores(),
                           selfassesment=selfassesment,
                           how_hany_trais=how_hany_trais)

@main.route("/results_bars")
@login_required
@register_menu(main, '.results_bars', 'Results bars', order=6,
               visible_when=lambda: current_user.is_authenticated)
def results_bars():
    rangee = [0,1]
    range2 = [2,3]
    text = ["Test results",
            "Genomelink data",
            "Self-assesment results",
            "Friends assesment"]
    answers = [mean_user_scores_percentage(),
               [int(x*100/5) for x in genome()[1].get("datasets")[0].get("data")],
               selfassesmenttraitsresults(),
               friend_mean_user_scores_percentage()]
    colours = ['#e95095', '#ffcc00', 'orange', 'deepskyblue', 'green']
    return render_template('all_in_one_results_bar.html',
                           trait=handled_traits,
                           colours=colours,
                           data=zip(range(len(text)), text, answers))

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


# @main.route("/userprofile", methods=['GET', 'POST'])
# @login_required
# @register_menu(main, '.userprofile', 'Your profile', order=7,
#                visible_when=lambda: current_user.is_authenticated)
# def userprofile():
#     '''userprofile'''
#
#     return render_template('userprofile.html', user=current_user)
#


@login_required
@main.route('/upload_image', methods=['GET', 'POST'])
def upload_file():
    try:                                #go 1st to this upload, then do the rest of the code
        file=request.files['image']
    except KeyError:
        return render_template("upload_image.html")
    file.filename = current_user.username+".jpg"    #rename to username.jpg -important for the rest functions
    f = os.path.join(app.app.config['UPLOAD_FOLDER'], file.filename)
    file.save(f)
    return render_template('index.userprofile')



@main.route("/userprofile", methods=['GET', 'POST'])
@login_required
@register_menu(main, '.userprofile', 'Your profile', order=7,
               visible_when=lambda: current_user.is_authenticated)
def userprofile():
    '''userprofile'''
    form = SearchForm(request.form)
    # Search friend on submit
    if form.validate_on_submit():
        searchfriend = form.searchfriend.data.split()
        if len(searchfriend) == 0:
            flash('You have to write name or/and surname', 'warning')
        else:
            messages = ",".join(searchfriend)
        session['messages'] = messages
        return redirect(url_for('main.search', messages=messages))

    return render_template('userprofile.html', user=current_user, form=form)


@main.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    '''searchresults'''
    text ="" #text which will be displayed if no search results
    user_id = current_user.id
    form_request = FriendRequest()
    messages = session['messages'].split(',')
    flt = make_filter([User.surname, User.name], messages)
    results = User.query.with_entities(User.surname,
                                       User.name,
                                       User.id,
                                       User.email,
                                       User.username).filter(flt).all()
    current_user_friends = [x.friend_id for x in Friends.query.filter_by(user_id=current_user.id).all()]
    results = [x for x in results if not x[2] in current_user_friends] #add only firends which are not in your friends already
    if len(results)==0:
        text = "No new friends with this data :)"

    # Adding friends to DB
    if form_request.is_submitted():
        friend_id = request.form['submit']
        is_friend = db.session.query(Friends).filter_by(user_id= current_user.id).filter_by(friend_id=friend_id).first()
        if user_id == friend_id:
            flash('You can not add yourself')
        elif is_friend:
            flash('You are friends already')
        else:
            flash('You send friend request')
            # connection = Friends(user_id=int(user_id),
            #                     friend_id=int(friend_id),
            #                      requestfriend=False)
            # db.session.add(connection)
            connection_back = Friends(user_id=int(friend_id),   #if you are my friends, I am your too
                                 friend_id=int(user_id),
                                      requestfriend=False)
            db.session.add(connection_back)
            db.session.commit()
    return render_template('search.html', results=results, form=form_request, user_id=user_id, user=current_user, text=text)


@main.route("/user_friends", methods=['GET', 'POST'])
@login_required
@register_menu(main, '.user_friends', 'Your friends', order=8,
               visible_when=lambda: current_user.is_authenticated)
def user_friends():
    form = FriendRequest()
    if form.is_submitted():
        if request.form['submit'].split()[0] == 'submit':
            session['id'] = request.form['submit'].split()[1]
            return redirect(url_for('main.friend_profile'))
        else:
            session['id']=request.form['submit']    #send friend ID to fiendassesment to know which friend to assess
            return redirect(url_for("main.friend_choose_trait_test")) #could be friendasessment and will be ok too!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    text=""
    '''Show how this user asses you.'''
    user_friends= [User.query.filter_by(id=x.friend_id).first() for x in Friends.query.filter_by(user_id=current_user.id, requestfriend=1).all()] #search all friends
    user_firends_which_user_answered_id = set([x.user_id for x in FriendAnswer.query.filter_by(friend_id=current_user.id)])
    list_of_answers =[]
    for friend in user_friends:
        if friend.id in user_firends_which_user_answered_id :
            list_of_answers.append([user_answer_for_friend(trait, friend.id) for trait in handled_traits])
        else:
            list_of_answers.append([0,0,0,0,0])
    # flash(list_of_answers)
    # return redirect(url_for('main.index'))
    results_from_friend= [user_answer_for_friend(trait, current_user.id) for trait in handled_traits]

    if not user_friends:
        text="There are no friends yet:< Try to find some!"
    done=False######################################################################################################################################
    colors = ["#e95095", "#ffcc00", "orange", "deepskyblue", "green"]
    return render_template('user_friends.html', results=user_friends, user_id=current_user, text=text, form=form,
                           results_from_friend=results_from_friend, user_firends_which_answered_id=user_firends_which_user_answered_id,
                           done=done, list_of_answers=list_of_answers, colours=colors, trait=handled_traits)

@main.route("/friend_profile", methods=['GET', 'POST'])
@login_required
def friend_profile():
    data=0
    form = ChooseTraitTestForm()
    friend_id = session['id']
    friend = db.session.query(User).filter_by(id=friend_id).first()
    done_request = db.session.query(FriendAnswer).filter_by(user_id=current_user.id, friend_id=friend_id).first()
    done=False
    if done_request:
        done=True
        data= friend_mean_user_scores_percentage()
    if form.is_submitted():
        friend=db.session.query(Friends).filter_by(user_id=friend_id, friend_id=current_user.id).first()
        friend.testrequest=True
        db.session.commit()
        flash("The request has been sent","info")
        return redirect(url_for('main.index'))
    colours = ['#e95095', '#ffcc00', 'orange', 'deepskyblue', 'green']
    text="This friend's assemsent on you"
    genomee = [int(x*100/5) for x in genome()[1].get("datasets")[0].get("data")]
    return render_template('friend_profile.html', result=friend, form=form, done=done, trait=handled_traits,
                           colours=colours, text= text, data=data,results_from_friend=data,
                           genome = genomee)
'''We dont use it, but it works fine if we weill want to'''
#
# x=0
# ans=[0 for x in handled_traits]
# @main.route("/friendasessment", methods=['GET', 'POST'])
# @login_required
# def friendasessment():
#     '''Friend assesment bars questionaire - from 1 to 5 how is he'''
#     friend_id = session['id']
#     name = User.query.filter_by(id=friend_id).first() #name to diplay "How do u think user is
#     #this 2 global are bad, but it is working, so lets left it here
#     global x
#     global ans
#     traits = handled_traits #take trait tuple
#     form= SelfAssesmentBarsForm()
#
#     #if user dont answer to all traits
#     if x < len(traits):
#         trait = traits[x]
#         # if form.validate_on_submit():
#         if form.is_submitted():
#             ans[x]=int(form.answers.data)*20 #to make it from 20% to 100%
#             x+=1
#             # take next trait
#         try:
#             trait = traits[x]   #at the end, the index will be out of handled_traits tuple, so. Here it is neccessary to noc answer first question 2 times at the beggining.
#             return render_template('selfassesmentbar.html', form=form, trait=trait, user=name, visible=True) # go next trait quiz
#         except IndexError:
#             pass
#
#     friend_traits= db.session.query(FriendAssesment).filter_by(friend_id=current_user.id).filter_by(user_id=friend_id).first()
#     if friend_traits: #if user already answered to questions change his answer to new one
#         friend_traits.agreeableness=ans[0]
#         friend_traits.conscientiousness=ans[1]
#         friend_traits.extraversion =ans[2]
#         friend_traits.neuroticism=ans[3]
#         friend_traits.openness=ans[4]
#     else: #if not, add him to database
#         sat= FriendAssesment(agreeableness=ans[0], conscientiousness=ans[1], extraversion =ans[2],
#                                  neuroticism=ans[3], openness=ans[4], user_id =friend_id, friend_id=current_user.id)
#         db.session.add(sat)
#     db.session.commit()
#     x=0
#     flash("You made an assesment of your friend.")
#     return redirect(url_for('main.user_friends'))
#







@main.route("/friend_choose_trait_test", methods=['GET', 'POST'])
@login_required
# @register_menu(main, '.friend_choose_trait_test', 'Friend Personality test', order=11,
#                visible_when=lambda: current_user.is_authenticated)
def friend_choose_trait_test():
    '''Choose trait in wchich user will answer to traits about his friends.'''
    colors = ["#e95095", "#ffcc00", "orange", "deepskyblue", "green"]
    b_colors = ["#e95095", "#ffcc00", "orange", "deepskyblue", "green"]
    form = ChooseTraitTestForm()
    if form.is_submitted():
        return redirect(url_for("main.friend_questionare", trait=request.form['submit']))
    return render_template("choose_trait_test.html", handled_traits=handled_traits, form=form, colors=colors[::-1], b_colors=b_colors[::-1])



@main.route("/friend_questionare", methods=['GET', 'POST'])
@login_required
def friend_questionare():
    '''Show test where user can judge his friends'''
    # next_id = 0
    friend_id = session['id']
    name = User.query.filter_by(id=friend_id).first() #name to diplay "How do u think user is
    trait = request.args['trait']        #take trait from choose_trait_test button that was clicked
    form = QuestionareForm()
    #adding answet to db
    if form.is_submitted():
        #If in db is answer for this question update it in not just add.
        anser_in_database =db.session.query(FriendAnswer).filter_by(user_id=friend_id, question_id=form.id.data, friend_id=current_user.id).first() #request of which friend !!!!!!!!!!!!!!!!!!!!!
        if anser_in_database:
            anser_in_database.answer=int(form.answers.data) + 1
            anser_in_database.score=db.session.query(Choice).filter_by(trait_id=form.id.data)[int(form.answers.data)].score
        else:
            answer = FriendAnswer(question_id=form.id.data,
                            answer=int(form.answers.data) + 1,
                            user_id=friend_id,
                            friend_id= current_user.id,
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
        my_answers = FriendAnswer.query.filter_by(friend_id=current_user.id, user_id=friend_id)
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
        'count': (number_of_questions)}
    return render_template('questionare.html', data=data, form=form, user=name, visible=True)


@cache.cached(timeout=360000)
@main.route('/tos')
def tos():
    return render_template('tos.html')


@main.route("/friend_request", methods=['GET', 'POST'])
@login_required
@register_menu(main, '.friend_request', 'Friend Requests', order=9,
               visible_when=lambda: current_user.is_authenticated)
def friend_request():
    form = FriendRequest()
    if form.is_submitted():
        friend_id=request.form['submit']
        if request.form['status'].strip() == 'refuse':
            if isrequest(current_user.id, friend_id):
                fquery = Friends.query.filter_by(user_id =current_user.id, friend_id = friend_id).one()
                db.session.delete(fquery)
                db.session.commit()
                flash("Your friend request refused", "info")
        elif request.form['status'].strip() == 'accept':

            fquery2 = db.session.query(Friends). \
                filter_by(user_id=current_user.id,
                          friend_id=friend_id,
                          requestfriend=False). \
                first()


            # return redirect(url_for('main.index'))
            fquery2.requestfriend = True
            friend = Friends(user_id=int(friend_id), friend_id=int(current_user.id), requestfriend=True)
            db.session.add(friend)
            db.session.commit()
            flash("Your friend request succesfully accepted", "info")
        else:
            flash("An error occured during addition of friend")
    text=""
    friendrequests1 = [x.friend_id for x in db.session.query(Friends).filter_by(user_id=current_user.id, requestfriend=False).all()]
    friendrequests = [db.session.query(User).filter_by(id=x).first() for x in friendrequests1]
    if not user_friends:
        text="There are no friends requests yet:<"
    return render_template('friend_request.html', results=friendrequests, user_id=current_user, text=text, form=form )



def isrequest(user_id, friend_id):
    """
    Checks whether friend request status is:
    True if the request is still pending
    False if the request is accepted
    """
    friendrequest = db.session.query(Friends).filter(or_(Friends.user_id == user_id, Friends.user_id == friend_id),
                                                    or_(Friends.friend_id == friend_id, Friends.friend_id == user_id),
                                                    Friends.requestfriend == False).first()
    if friendrequest:
        return True
    else:
        return False


def getrecivedreq(user_id):
    """
    Returns users from which user recived friend request.
    """
    receive = db.session.query(User).filter(Friends.user_id == user_id,
                                           Friends.requestfriend == False).join(Friends,
                                           Friends.user_id == User.id).all()
    return receive


@main.route("/test_request", methods=['GET', 'POST'])
@login_required
@register_menu(main, '.test_request', 'Test Requests', order=10,
               visible_when=lambda: current_user.is_authenticated)
def friend_request_test():
    form = FriendRequest()
    if form.is_submitted():
        if request.form['submit']:
            session['id'] = request.form['submit']
            friend = db.session.query(Friends).filter_by(user_id=int(session['id']), friend_id=current_user.id).first()
            friend.testrequest = False
            db.session.commit()
            return redirect(url_for('main.friend_choose_trait_test'))

    text=""
    friendrequests1 = [x.friend_id for x in db.session.query(Friends).filter_by(user_id=current_user.id, testrequest=True).all()]
    friendrequests = [db.session.query(User).filter_by(id=x).first() for x in friendrequests1]
    if not user_friends:
        text="There are no friends requests"
    return render_template('test_request.html', results=friendrequests, user_id=current_user, text=text, form=form )
