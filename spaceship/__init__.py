from flask import Flask
app = Flask(__name__)

from . import logs

from .config import Config
app.config.from_object(Config)

from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

from . import enforce_ssl
from . import enforce_www
from . import google_auth
from . import db
from . import login
from . import views

