from flask_testing import TestCase
from app import create_app, db, yaml
from app.models import User, Question, GLTrait
from lxml import etree


class ViewTestCase(TestCase):

    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = 'development'
    TESTING = True

    def create_app(self):
        return create_app(self)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestLogin(ViewTestCase):

    USER = {'username': 'mike',
            'email': 'mike@dot.com',
            'name' : 'Michael',
            'surname': 'Engel',
            'password': 'mike123'}

    def setUp(self):

        super(TestLogin, self).setUp()

        app = self.create_app()
        self.client = app.test_client()

        # Need the CSRF token
        response = self.client.get('/login')
        out = response.data.decode('UTF-8')
        tree = etree.HTML(out)
        tok = tree.xpath('//input[@name="csrf_token"]/@value')[0]

        self.data = {'username': self.USER['username'],
                     'password': self.USER['password'],
                     'csrf_token': tok}

    def test_login_user_unconfirmed(self):

        user = User(**self.USER)
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/login', data=self.data,
                                    follow_redirects=True)
        self.assertIn("You have to confirm your email",
                      response.data.decode('UTF-8'))

    def test_login_user_confirmed(self):

        user = User(**self.USER)
        user.confirmed = 1
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/login', data=self.data,
                               follow_redirects=True)
        self.assertIn("Logged in successfully",
                      response.data.decode('UTF-8'))
