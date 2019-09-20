
# create the flask app
from flask import Flask
app = Flask(__name__)

# configure logging
from spaceship import logs

# configure the app
from spaceship.config import Config
app.config.from_object(Config)

# CSRF protection
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# handling of redirects and static files
from spaceship import assets
from spaceship import enforce_ssl
from spaceship import enforce_www

# load the db and redis
from spaceship import db
from spaceship import redis

# these things depend on the db and so go after it
from spaceship import login
from spaceship import google_auth
from spaceship import views

# tasktiger configuration (for delayed tasks)
from spaceship import tasktiger
