from flask import Flask
app = Flask(__name__)

from . import logs

from .config import Config
app.config.from_object(Config)

from . import enforce_ssl
from . import db
from . import login
from . import views

