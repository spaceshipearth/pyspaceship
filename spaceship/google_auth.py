
from authlib.flask.client import OAuth
from flask_login import login_user
from flask import redirect, session, url_for
from loginpass import create_flask_blueprint, Google

from spaceship import app
from spaceship.models import User

oauth = OAuth(app)

def handle_authorize(remote, token, user_info):
  next_url = session.pop('oauth_next_url', url_for('home'))
  if user_info:
    session['oauth_user_info'] = user_info
  return redirect(next_url)

google_bp = create_flask_blueprint(Google, oauth, handle_authorize)
app.register_blueprint(google_bp, url_prefix='/google')
