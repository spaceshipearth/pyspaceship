
from flask import request, flash, redirect, url_for
from flask_login import LoginManager

from . import app

from .models.user import User

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
  return User.get_by_id(int(user_id))

@login_manager.unauthorized_handler
def handle_needs_login():
  flash({'msg':"You have to be logged in to access this page.", 'level':'warning'})

  next=url_for(request.endpoint, **request.view_args)
  return redirect(url_for('login', next=next))
