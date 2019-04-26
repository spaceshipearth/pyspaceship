from flask import Flask
from authlib.flask.client import OAuth
from loginpass import create_flask_blueprint, Google

app = Flask(__name__)
oauth = OAuth(app)

def handle_authorize(remote, token, user_info):
  if token:
    print(remote.name, token)
  if user_info:
    print(f'should save {user_info}')

google_bp = create_flask_blueprint(Google, oauth, handle_authorize)
app.register_blueprint(google_bp, url_prefix='/google')
