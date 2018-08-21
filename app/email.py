from flask_mail import Message

import app
# from app import mail


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender="pwrgl2confirm@gmail.com"
    )
    app.mail.send(msg)

    if __name__ == '__main__':
        with app.app_context():
            msg = Message(subject="Hello",
                          sender=app.config.get("MAIL_USERNAME"),
                          recipients=["jasiuimperator@gmail.com"],  # replace with your email for testing
                          body="This is a test email I sent with Gmail and Python!")
            mail.send(msg)