from . import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    '''Table for storing registered users'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    #password = db.Column(db.Binary(256), nullable=False)
    password = db.Column(db.String(256), nullable=False)

    gltrait = db.relationship("GLTraits", back_populates='user')
    answer = db.relationship("Answers", back_populates='author')

    def __repr__(self):
        form = "User(id = {}, username = {})"
        return form.format(self.id, self.username)


class GLTraits(db.Model):
    '''Local storage for personality-related traits obtained from
    Genomelink API'''
    id = db.Column(db.Integer, primary_key=True)
    trait = db.Column(db.String)
    t_score = db.Column(db.Integer)   # Score for every trait eg. 1-5
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates="gltrait")


class Questions(db.Model):
    '''Table for storing questions related to personality traits'''
    id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String)
    trait = db.Column(db.String)
    answer = db.relationship("Answers", back_populates="question")


class Answers(db.Model):
    '''Table for storing user's answers to the questions.
    Includes self-assessment and replies from other users.'''
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    answer = db.Column(db.Integer)  # eg. 1-5
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question = db.relationship("Questions", back_populates="answer")
    author = db.relationship("User", back_populates="answer")
