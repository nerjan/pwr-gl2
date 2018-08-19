# pwr-gl2

**pwr-gl2** is a working name, we'll change it later, when we know what the
app is doing and come up with a fancy name.

## How to run

First, clone it, set up virtual environment and install requirements:

```
$ git clone https://github.com/boryszef/pwr-gl2.git
$ cd pwr-gl2
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Download the `config.ini` file with key of our app (not included in the repo)
and place it in the top directory.

First, make sure the database is built and perform migrations (if any):
```
export FLASK_APP=app
export FLASK_DEBUG=1
flask db init
flask db migrate
flask db upgrade
```

Finally, run the app:

```
python run.py
```

## Testing

Testing uses additional modules: `Flask-Testing` and `selenium`. Testing the
frontend with selenium can be tricky. You need a matching set of `selenium`,
`firefox` and `geckodriver`. The latter one can be found here:
https://github.com/mozilla/geckodriver/releases
A working combination of those three is Firefox 60, Selenium 3.13 and
geckodriver 0.21. Test can be run automatically:
```
python -m unittest
```
