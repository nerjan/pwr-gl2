from .extensions import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    '''Table for storing registered users'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    #password = db.Column(db.Binary(256), nullable=False)
    password = db.Column(db.String(256), nullable=False)

    gltrait = db.relationship("GLTrait", back_populates='user')
    answers = db.relationship("Answer", back_populates='author')

    def __repr__(self):
        form = "User(id = {}, username = {})"
        return form.format(self.id, self.username)


class GLTrait(db.Model):
    '''Local storage for personality-related traits obtained from
    Genomelink API'''
    id = db.Column(db.Integer, primary_key=True)
    trait = db.Column(db.String)
    t_score = db.Column(db.Integer)   # Score for every trait eg. 1-5
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="gltrait")


class Question(db.Model):
    '''Table for storing questions related to personality traits'''
    id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String)
    trait = db.Column(db.String)
    answers = db.relationship("Answer", back_populates="question")


class Answer(db.Model):
    '''Table for storing user's answers to the questions.
    Includes self-assessment and replies from other users.'''
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    answer = db.Column(db.Integer)  # eg. 1-5
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question = db.relationship("Question", back_populates="answers")
    author = db.relationship("User", back_populates="answers")
