from flask import Flask, render_template, request
from flask import redirect, url_for, flash, session
import genomelink
import configparser
import os


app = Flask(__name__)


traits = ('agreeableness', 'conscientiousness', 'extraversion', 'neuroticism',
          'openness')


@app.route("/")
def index():
    '''Display main view of the app'''

    scope = ['report:{}'.format(t) for t in traits]
    authorize_url = genomelink.OAuth.authorize_url(scope=scope)

    menu = [
        {'title': 'Genomic insight', 'url': url_for('genome')},
        {'title': 'Self-assessment questionare',
         'url': url_for('questionare')},
        {'title': 'Self-assessment results',
         'url': url_for('selfassessment')}
    ]
    return render_template('index.html', authorize_url=authorize_url,
                           menu=menu)


@app.route("/login")
def login():
    pass


@app.route("/logout")
def logout():
    pass


@app.route("/genome")
def genome():
    '''Display genomic insight based on GenomeLink API'''

    reports = []
    if session.get('oauth_token'):
        for name in traits:
            reports.append(genomelink.Report.fetch(
                                name=name,
                                population='european',
                                token=session['oauth_token']))

    return render_template('genome.html', reports=reports,
                           main_url=url_for('index'))


@app.route("/questionare")
def questionare():
    '''Show self-assessment questionare'''
    pass


@app.route("/selfassessment")
def selfassessment():
    '''Show self-assessment results'''
    pass


@app.route("/callback")
def callback():

    try:
        token = genomelink.OAuth.token(request_url=request.url)

    except genomelink.errors.GenomeLinkError as e:
        flash('Authorization failed.')
        if os.environ.get('DEBUG') == '1':
            flash('[DEBUG] ({}) {}'.format(e.error, e.description))
        return redirect(url_for('index'))

    session['oauth_token'] = token
    return redirect(url_for('index'))


def prepare_env():
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read('config.ini')
    for key in config['global']:
        val = config['global'][key]
        os.environ[key] = val


prepare_env()
app.secret_key = os.urandom(24)


if __name__ == '__main__':
    app.run(debug=True)
