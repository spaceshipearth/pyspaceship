
from flask import request, flash, redirect, url_for
from flask_login import LoginManager

from . import app

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def handle_needs_login():
  flash({'msg':"You have to be logged in to access this page.", 'level':'warning'})
  return redirect(url_for('login', next=request.endpoint))
