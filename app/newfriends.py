from .models import User, Friends
from .extensions import db, or_


def isfriend(user_id, friend_id):
    """
    Checks whether user has already the requested friend.
    True if the user is your accepted friend
    False if the user is not your friend
    """
    session = db.Session()
    isfriend = db.session.query(Friends).filter(or_(Friends.user_id == user_id, Friends.user_id == friend_id),
                                               or_(Friends.friend_id == friend_id, Friends.friend_id == user_id),
                                               Friends.request == True).first()
    if isfriend:
        return True
    else:
        return False

def isrequest(user_id, friend_id):
    """
    Checks whether friend request status is:
    True if the request is still pending
    False if the request is accepted
    """
    friendrequest = db.session.query(Friends).filter(or_(Friends.user_id == user_id, Friends.user_id == friend_id),
                                                    or_(Friends.friend_id == friend_id, Friends.friend_id == user_id),
                                                    Friends.request == False).first()

    if friendrequest:
        return True
    else:
        return False



def getrecivedreq(user_id):
    """
    Returns users from which user recived friend request.
    """

    receive = db.session.query(User).filter(Friends.friend_id == user_id,
                                           Friends.request == False).join(Friends,
                                           Friends.user_id == User.id).all()

    return receive


def getsentreq(user_id):
    """
    Returns users to which user sent friend reuqest.
    """

    sent = db.session.query(User).filter(Friends.user_id == user_id,
                                           request == False).join(Friends,
                                           Friends.friend_id == User.id).all()

    return sent

def getfriends(user_id):
    """
    It returns user's friends
    """

    friendquery = db.session.query(User).filter(Friends.user_id == user_id,
                                           Friends.request == True).join(Friends,
                                           Friends.friend_id == User.id).all()

    return friendquery
