from flask import Flask

app = Flask(__name__)

from spaceship.config import Config
app.config.from_object(Config)

from spaceship import logs

from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

from spaceship import assets
from spaceship import enforce_ssl
from spaceship import enforce_www
from spaceship import google_auth
from spaceship import db
from spaceship import login
from spaceship import views

