
from itsdangerous import URLSafeTimedSerializer

from spaceship.config import Config

def generate_confirmation_token(email):
    """Confirmation email token."""
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.dumps(email, salt=Config.EMAIL_CONFIRM_SALT)

def confirm_token(token, expiration=3600):
    """Plausibility check of confirmation token."""
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.loads(token, salt=Config.EMAIL_CONFIRM_SALT, max_age=expiration)
