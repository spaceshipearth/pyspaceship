
from flask import render_template, url_for
import logging
from typing import Any, Dict, Optional

from spaceship import email as email_sender
from spaceship.create_team import create_team
from spaceship.confirm_email import generate_confirmation_token
from spaceship.models import User

log = logging.getLogger('spaceship.login_or_register')

class Error(Exception):
  """generic register exception"""
  pass

class LoginFailed(Error):
  """when password doesn't match and oauth info is missing"""
  pass

def login(
    email: Optional[str] = None, password: Optional[str] = None, oauth_user_info: Optional[Dict[str, Any]] = {}) -> User:
  """Logs a user in"""
  email = oauth_user_info.get('email', email)

  # if the user does not exist, cannot log in
  user = User.query.filter(User.email == email).first()
  if not user:
    raise LoginFailed()

  # can we log in via oauth?
  if oauth_user_info and oauth_user_info.get('email') == user.email:
    return user

  # log in using a password?
  elif password and user.check_password(password):
    return user

  # out of options, cannot log in
  else:
    raise LoginFailed()

def register(email=None, name=None, password=None, oauth_user_info={}, as_captain=False):
  """registers or logs the user in"""
  # no matter what, we require an email address; default to the oauth one if available
  email = oauth_user_info.get('email', email)
  if not email:
    raise Error('email is required')

  # if the user already exists, log them in
  u = User.query.filter(User.email == email).first()
  if u:
    return login(email, password, oauth_user_info)

  # if we got here, we have to create the user
  u = User(email=email)
  u.name = oauth_user_info.get('name', name if name else email.split('@')[0])
  u.email_confirmed = email == oauth_user_info.get('email')
  if password:
    u.set_password(password)
  u.save()

  # create a team for the user if they went through the Register (aka Become a Captain) flow
  if as_captain:
    create_team(u)

  # send email confirmation
  if not u.email_confirmed:
    token = generate_confirmation_token(u.email)
    email_sender.send.delay(
      to_emails=u.email,
      subject='Please verify your email for Spaceship Earth',
      html_content=render_template(
        'confirm_email.html',
        user=u,
        confirmation_url=url_for('confirm_email', token=token, _external=True)
      )
    )

  # return the user we created
  return u
