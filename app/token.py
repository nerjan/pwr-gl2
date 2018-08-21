
from itsdangerous import URLSafeTimedSerializer
import app
# import app.config as config


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.app.config.get("SECRET_KEY"))
    return serializer.dumps(email, salt=app.app.config.get("SECURITY_PASSWORD_SALT"))


def confirm_token(token, expiration=86000):
    serializer = URLSafeTimedSerializer(app.app.config.get("SECRET_KEY"))
    try:
        email = serializer.loads(
            token,
            salt=app.app.config.get("SECURITY_PASSWORD_SALT"),
            max_age=expiration
        )
    except:
        return False
    return email