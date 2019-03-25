from flask import Flask
app = Flask(__name__)

from .config import Config
app.config.from_object(Config)

from . import db
from . import login
from . import views
