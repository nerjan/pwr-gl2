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

    scope = [ 'report:{}'.format(t) for t in traits ]
    authorize_url = genomelink.OAuth.authorize_url(scope=scope)

    reports = []
    if session.get('oauth_token'):
        for name in traits:
            reports.append(genomelink.Report.fetch(name=name,
                                                   population='european',
                                                   token=session['oauth_token']))

    return render_template('index.html', authorize_url=authorize_url,
                           reports=reports)


@app.route('/callback')
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
    config.optionxform=str
    config.read('config.ini')
    for key in config['global']:
        val = config['global'][key]
        os.environ[key] = val


if __name__ == '__main__':
    prepare_env()
    app.secret_key = os.urandom(24)
    app.run(debug=True)
