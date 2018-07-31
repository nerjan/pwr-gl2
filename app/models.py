from . import db


class User(db.Model):
    '''Table for storing registered users'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Binary(256), nullable=False)


class GLTraits(db.Model):
    '''Local storage for personality-related traits obtained from
    Genomelink API'''
    id = db.Column(db.Integer, primary_key=True)


class Questions(db.Model):
    '''Table for storing questions related to personality traits'''
    id = db.Column(db.Integer, primary_key=True)


class Answers(db.Model):
    '''Table for storing user's answers to the questions.
    Includes self-assessment and replies from other users.'''
    id = db.Column(db.Integer, primary_key=True)
