from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    '''Table for storing registered users'''

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(120),  nullable=True, default="noname")
    surname = db.Column(db.String(120),  nullable=True, default="nosurname")
    confirmed = db.Column(db.Boolean, nullable=False, default=False) # to confirm email

    gltrait = db.relationship("GLTrait", back_populates='user')
    answers = db.relationship("Answer", back_populates='author')
    self_assesment_traits = db.relationship("SelfAssesmentTraits", back_populates="user")


    def __init__(self, username, email, password, name, surname):
        self.username = username
        self.email = email
        self.set_password(password)
        self.name = name
        self.surname = surname

    def __repr__(self):
        form = "User(id = {}, username = {})"
        return form.format(self.id, self.username)

    @property
    def is_authenticated(self):
        # Flask-Login needs this; probably for the remember-me feature
        return bool(self.authenticated)

    @property
    def is_active(self):
        # A place-holder, required by Flask-Login.
        # Always return True, until we implement this feature
        return True

    @property
    def is_anonymous(self):
        # Required by Flask-Login; we don't support anonymous users
        return False

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class GLTrait(db.Model):
    '''Local storage for personality-related traits obtained from
    Genomelink API'''

    id = db.Column(db.Integer, primary_key=True)
    trait = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    t_score = db.Column(db.Integer)   # Score for every trait eg. 1-5
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="gltrait")

    def serialize(self):
        return {'name': self.trait,
                'description': self.description,
                'score': self.t_score}


class Question(db.Model):
    '''Table for storing questions related to personality traits'''

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(1000))
    weight = db.Column(db.Integer)
    trait = db.Column(db.String(100))
    impact = db.Column(db.String(20))
    choices = db.relationship("Choice", back_populates="question")
    answers = db.relationship("Answer", back_populates="question")
    friend_answer= db.relationship("FriendAnswer", back_populates="question")


def Question_constructor(loader, node):
    values = loader.construct_mapping(node, deep=True)
    return Question(**values)


class Choice(db.Model):
    '''Possible answers to Questions that user will be offered to choose
    from'''

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(1000))
    score = db.Column(db.Integer)
    trait_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    question = db.relationship("Question", back_populates="choices")
    answers = db.relationship("Answer", back_populates="choice")
    friend_answer  = db.relationship("FriendAnswer", back_populates="choice")


def Choice_constructor(loader, node):
    values = loader.construct_mapping(node, deep=True)
    return Choice(**values)


class Answer(db.Model):
    '''Table for storing user's answers to the questions.
    Includes self-assessment and replies from other users.'''

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    score = db.Column(db.Integer, db.ForeignKey('choice.score'))  #  It is better, because we anyway need only score
    answer = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question = db.relationship("Question", back_populates="answers")
    author = db.relationship("User", back_populates="answers")
    choice = db.relationship("Choice", back_populates="answers")


class SelfAssesmentTraits(db.Model):
    '''Table for storing self assesment traits'''

    id = db.Column(db.Integer, primary_key=True)
    agreeableness = db.Column(db.Integer)
    conscientiousness = db.Column(db.Integer)
    extraversion = db.Column(db.Integer)
    neuroticism = db.Column(db.Integer)
    openness = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="self_assesment_traits")


class Friends(db.Model):
    '''Associative table to store friends of user'''

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    requestfriend = db.Column(db.Boolean, nullable=False)

    user = db.relationship("User", foreign_keys=[user_id], uselist=False)
    friend = db.relationship("User", foreign_keys=[friend_id], uselist=False)

class FriendAssesment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id')) #who judge
    agreeableness = db.Column(db.Integer)
    conscientiousness = db.Column(db.Integer)
    extraversion = db.Column(db.Integer)
    neuroticism = db.Column(db.Integer)
    openness = db.Column(db.Integer)

    user = db.relationship("User", foreign_keys=[user_id], uselist=False)
    friend = db.relationship("User", foreign_keys=[friend_id], uselist=False)


class FriendAnswer(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    score = db.Column(db.Integer, db.ForeignKey('choice.score'))  # It is better, because we anyway need only score
    answer = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))       #THis is our friend!!
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'))     #this is Us when we answer to someones test
    question = db.relationship("Question", back_populates="friend_answer")
    author = db.relationship("User", foreign_keys=[user_id], uselist=False)
    friend = db.relationship("User", foreign_keys=[friend_id], uselist=False)                   #????will it work??????
    choice = db.relationship("Choice", back_populates="friend_answer")
