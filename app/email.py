from flask_mail import Message
from .extensions import mail


def send_email(to, subject, template):
    msg = Message(subject,
                  recipients=[to],
                  html=template,
                  sender="pwrgl2confirm@gmail.com")
    mail.send(msg)
