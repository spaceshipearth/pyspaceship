from authlib.flask.client import OAuth
from loginpass import create_flask_blueprint, Google

from flask_login import login_user
from flask import redirect, url_for

from .models.user import User
from . import app
oauth = OAuth(app)

def handle_authorize(remote, token, user_info):
  if token:
    print(remote.name, token)
  if user_info:
    email = user_info['email']

    try:
      user = User.get(User.email == email)
    except User.DoesNotExist:
      user = User(email=email)
      user.save()

    login_user(user)

  return redirect(url_for('dashboard'))

google_bp = create_flask_blueprint(Google, oauth, handle_authorize)
app.register_blueprint(google_bp, url_prefix='/google')