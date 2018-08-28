"""empty message

Revision ID: 39405359d917
Revises: 
Create Date: 2018-08-23 00:29:05.166385

"""
from alembic import op
import sqlalchemy as sa

from app.models import User
from app import yaml, app_dir

# revision identifiers, used by Alembic.
revision = '39405359d917'
down_revision = None
branch_labels = None
depends_on = None

def add_data():
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)
    test_user = User(username='pkujawa',
                     email='pkujawa@example.com',
                     password='test',
                     name='Paulina',
                     surname='Kujawa')
    test_user.confirmed = True
    session.add(test_user)

    test_user = User(username='Janek',
                     email='Janek@example.com',
                     password='test',
                     name='Janek',
                     surname='Belkner')
    test_user.confirmed = True
    session.add(test_user)

    test_user = User(username='nerjan',
                     email='nerjan@example.com',
                     password='test',
                     name='Jan',
                     surname='Belkner')
    test_user.confirmed = True
    session.add(test_user)

    test_user = User(username='boryszef',
                     email='boryszef@example.com',
                     password='test',
                     name='Borys',
                     surname='Szefczyk')
    test_user.confirmed = True
    session.add(test_user)

    test_user = User(username='dwiczew',
                     email='dwiczew@example.com',
                     password='test',
                     name='Daniel',
                     surname='Wiczew')
    test_user.confirmed = True
    session.add(test_user)

    test_user = User(username='filon',
                     email='filon@example.com',
                     password='test',
                     name='Filon',
                     surname='Kujawa')
    test_user.confirmed = True
    session.add(test_user)

    test_user = User(username='test',
                     email='test@example.com',
                     password='test',
                     name='John',
                     surname='Smith')
    test_user.confirmed = True
    session.add(test_user)
    test_user = User(username='test1',
                     email='test1@example.com',
                     password='test',
                     name='John1',
                     surname='Smith1')
    test_user.confirmed = True
    session.add(test_user)
    test_user = User(username='test2',
                     email='test2@example.com',
                     password='test',
                     name='John2',
                     surname='Smith2')
    test_user.confirmed = True
    session.add(test_user)
    test_user = User(username='test3',
                     email='test3@example.com',
                     password='test',
                     name='John',
                     surname='Smith')
    test_user.confirmed = True
    session.add(test_user)
    test_user = User(username='test4',
                     email='test4@example.com',
                     password='test',
                     name='John',
                     surname='Smith2')
    test_user.confirmed = True
    session.add(test_user)
    test_user = User(username='test5',
                     email='test5@example.com',
                     password='test',
                     name='John',
                     surname='Smith2')
    test_user.confirmed = True
    session.add(test_user)
    test_user = User(username='test6',
                     email='test6@example.com',
                     password='test',
                     name='John',
                     surname='Smith2')
    test_user.confirmed = True
    session.add(test_user)
    test_user = User(username='test7',
                     email='test7@example.com',
                     password='test',
                     name='John',
                     surname='Smith2')
    test_user.confirmed = True
    session.add(test_user)
    test_user = User(username='test8',
                     email='test8@example.com',
                     password='test',
                     name='John',
                     surname='Smith2')
    test_user.confirmed = True
    session.add(test_user)
    with open(app_dir+"/openness.yml") as fp:
        questions = yaml.load(fp.read())
    session.add_all(questions)
    session.commit()
    with open(app_dir+"/conscientiousness.yml") as fp:
        questions = yaml.load(fp.read())
    session.add_all(questions)
    session.commit()
    with open(app_dir+"/agreableness.yml") as fp:
        questions = yaml.load(fp.read())
    session.add_all(questions)
    session.commit()
    with open(app_dir+"/extraversion.yml") as fp:
        questions = yaml.load(fp.read())
    session.add_all(questions)
    session.commit()
    with open(app_dir+"/neuroticism.yml") as fp:
        questions = yaml.load(fp.read())
    session.add_all(questions)
    session.commit()



def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('question',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=1000), nullable=True),
    sa.Column('weight', sa.Integer(), nullable=True),
    sa.Column('trait', sa.String(length=100), nullable=True),
    sa.Column('impact', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.Column('authenticated', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('surname', sa.String(length=120), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('choice',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=1000), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('trait_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['trait_id'], ['question.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('friends',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('friend_id', sa.Integer(), nullable=True),
    sa.Column('requestfriend', sa.Boolean(), nullable=False),
    sa.Column('testrequest', sa.Boolean()),
    sa.ForeignKeyConstraint(['friend_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('friend_assesment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('friend_id', sa.Integer(), nullable=True),
    sa.Column('agreeableness', sa.Integer(), nullable=True),
    sa.Column('conscientiousness', sa.Integer(), nullable=True),
    sa.Column('extraversion', sa.Integer(), nullable=True),
    sa.Column('neuroticism', sa.Integer(), nullable=True),
    sa.Column('openness', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['friend_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gl_trait',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('trait', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('t_score', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('self_assesment_traits',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('agreeableness', sa.Integer(), nullable=True),
    sa.Column('conscientiousness', sa.Integer(), nullable=True),
    sa.Column('extraversion', sa.Integer(), nullable=True),
    sa.Column('neuroticism', sa.Integer(), nullable=True),
    sa.Column('openness', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('answer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('answer', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['question.id'], ),
    sa.ForeignKeyConstraint(['score'], ['choice.score'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('friend_answer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('answer', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('friend_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['question.id'], ),
    sa.ForeignKeyConstraint(['score'], ['choice.score'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['friend_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
    add_data()

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('answer')
    op.drop_table('self_assesment_traits')
    op.drop_table('gl_trait')
    op.drop_table('friends')
    op.drop_table('choice')
    op.drop_table('user')
    op.drop_table('question')
    # ### end Alembic commands ###
