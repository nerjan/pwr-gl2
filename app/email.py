from flask_mail import Message

import app


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender="pwrgl2confirm@gmail.com"
    )
    app.mail.send(msg)
