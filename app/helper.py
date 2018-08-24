from flask import flash, session
import genomelink
from flask_login import current_user
from .extensions import db, handled_traits
from .models import Choice
from .models import User, GLTrait, Question, Answer, SelfAssesmentTraits

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
        answer_choices= db.session.query(Choice).filter_by(trait_id=question.id)             #take all choices for this question
        max_score = max(x.score for x in answer_choices)                                     # take the biggest value of available choice score
        weight = question.weight                                                    #take question weight
        score += max_score*weight                                                   #add to max_score
    return score                                                                    #return one trait max score


def mean_user_scores_percentage():
    return [mean_user_score(x) for x in handled_traits] #in percentage

def mean_user_scores():
    return [int(x/100*5) for x in mean_user_scores_percentage()]                                             #for 5 step scale !!!!!!!!!

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


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash("%s" % (error))


