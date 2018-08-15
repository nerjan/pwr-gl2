from flask_testing import TestCase
from app import create_app, db
from app.models import *


class TestUser(TestCase):

    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = 'development'
    TESTING = True

    USER1 = {'username': 'mike',
             'email': 'mike@dot.com',
             'password': 'mike123'}

    USER2 = {'username': 'john',
             'email': 'john@dot.com',
             'password': 'john123'}

    USER3 = {'username': 'bob',
             'email': 'bob@dot.com',
             'password': 'bob123'}

    def create_app(self):
        return create_app(self)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_users_add(self):

        user = User(**self.USER1)
        db.session.add(user)
        db.session.commit()
        self.assertIn(user, db.session)

    def test_add_three_users(self):

        users = [User(**self.USER1),
                 User(**self.USER2),
                 User(**self.USER3)]
        db.session.add_all(users)
        db.session.commit()

        self.assertEqual(len(User.query.all()), 3)

    def test_check_password(self):

        user = User(**self.USER1)
        correct = self.USER1['password']
        incorrect = correct+"abc"
        
        self.assertTrue(user.check_password(correct))
        self.assertFalse(user.check_password(incorrect))
