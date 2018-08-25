from flask_testing import TestCase
from app import create_app, db, yaml
from app.models import User, Question, GLTrait, Friends


class ModelTestCase(TestCase):

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


class TestUser(ModelTestCase):

    USER1 = {'username': 'mike',
             'email': 'mike@dot.com',
             'password': 'mike123',
             'name': 'Mike',
             'surname': 'Smith'}

    USER2 = {'username': 'john',
             'email': 'john@dot.com',
             'password': 'john123',
             'name': 'John',
             'surname': 'Lemon'}

    USER3 = {'username': 'bob',
             'email': 'bob@dot.com',
             'password': 'bob123',
             'name': 'Bob',
             'surname': 'Harley'}

    def test_user_add(self):

        user = User(**self.USER1)
        db.session.add(user)
        db.session.commit()
        self.assertIn(user, db.session)

        q = User.query.first()
        self.assertEqual(q.username, self.USER1['username'])
        self.assertEqual(q.email, self.USER1['email'])

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


class TestQuestion(ModelTestCase):

    YAML = """
- !question
    value: Lorem ipsum
    weight: 1
    trait: latin
    impact: positive
    choices:
        - !answer
            value: yes
            score: 1
        - !answer
            value: no
            score: -1
- !question
    value: Quick brown fox
    weight: 1
    trait: english
    impact: negative
    choices:
        - !answer
            value: jumps
            score: 1
        - !answer
            value: swimms
            score: 2
"""

    def test_yaml_load(self):

        quest = yaml.load(self.YAML)

        self.assertEqual(len(quest), 2)
        self.assertEqual(quest[0].value, "Lorem ipsum")
        self.assertEqual(quest[0].trait, "latin")
        self.assertEqual(quest[0].impact, "positive")

    def test_add_question(self):

        question = "To be or not to be!"
        trait = "conscientiousness"
        impact = "negative"

        q1 = Question(value=question,
                      trait=trait,
                      impact=impact)
        db.session.add(q1)
        db.session.commit()

        q2 = Question.query.first()
        self.assertEqual(q2.value, question)
        self.assertEqual(q2.trait, trait)
        self.assertEqual(q2.impact, impact)


class TestGLTrait(ModelTestCase):

    def test_add_trait_for_user(self):

        mike = User(username='mike', password='123', email='mike@there.net', name='Mike', surname='Smith')
        db.session.add(mike)

        trait = 'openness'
        description = 'Lorem ipsum'
        t_score = 0
        tr = GLTrait(trait=trait, description=description, t_score=t_score,
                     user=mike)
        db.session.add(tr)
        db.session.commit()

        mike_tr = mike.gltrait[0]
        self.assertIs(mike_tr, tr)
        tr2 = GLTrait.query.first()
        self.assertEqual(tr2.user_id, mike.id)
        self.assertEqual(tr2.trait, trait)
        self.assertEqual(tr2.description, description)
        self.assertEqual(tr2.t_score, t_score)


class TestFriends(ModelTestCase):
    
    def test_add_friend(self):
        
        mike = User(username='mike', password='123', email='mike@there.net', name='Mike', surname='Smith')
        db.session.add(mike)

        john = User(username='john123', password='123', email='j@there.net', name='John', surname='Lemon')
        db.session.add(john)
        
        friends = Friends(mike, john)

        db.session.add(friends)
        db.session.commit()
