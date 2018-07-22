from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    '''Table for storing registered users'''
    __tablename__ = 'users'


class GLTraits(Base):
    '''Local storage for personality-related traits obtained from
    Genomelink API'''
    __tablename__ = 'gltraits'


class Questions(Base):
    '''Table for storing questions related to personality traits'''
    __tablename__ = 'questions'


class Answers(Base):
    '''Table for storing user's answers to the questions.
    Includes self-assessment and replies from other users.'''
    __tablename__ = 'answers'


if __name__ == '__main__':
    engine = create_engine('sqlite:///main.db')
    Base.metadata.create_all(engine)
