from flask import Flask
app = Flask(__name__)

from .config import Config
app.config.from_object(Config)

from . import logs

from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

from . import enforce_ssl
from . import enforce_www
from . import db
from . import login
from . import views

