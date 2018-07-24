from flask import Flask, render_template, request
from flask import redirect, url_for, flash, session
from flask_menu import Menu, register_menu
import genomelink
import configparser
import os


app = Flask(__name__)
Menu(app=app)


traits = ('agreeableness', 'conscientiousness', 'extraversion', 'neuroticism',
          'openness')


@app.route("/")
@register_menu(app, '.home', 'Home')
def index():
    '''Display main view of the app'''
    return render_template('index.html')


@app.route("/login")
def login():
    return render_template('index.html')


@app.route("/logout")
def logout():
    return render_template('index.html')


@app.route("/genome")
@register_menu(app, '.genome', 'Genomic insight')
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


@app.route("/questionare")
@register_menu(app, '.questionare', 'Self-assessment questionare')
def questionare():
    '''Show self-assessment questionare'''
    return render_template('index.html')


@app.route("/selfassessment")
@register_menu(app, '.selfassessment', 'Self-assessment results')
def selfassessment():
    '''Show self-assessment results'''
    return render_template('index.html')


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
    app.run(debug=True, host='0.0.0.0')
