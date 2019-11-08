import hashlib
import logging
import pendulum

from flask import render_template, flash, redirect, url_for, jsonify, request, session
from flask_login import login_user, logout_user, login_required, current_user

from sqlalchemy.exc import DatabaseError, IntegrityError
from urllib.parse import urlparse

from spaceship import app, email, achievements, team_invite, login_or_register
from spaceship.goals import GOALS_BY_CATEGORY
from spaceship.join_team import join_team
from spaceship.create_team import create_team
from spaceship.confirm_email import confirm_token
from spaceship.db import db
from spaceship.models import User, Team, TeamUser, Invitation, Goal, Mission, SurveyAnswer
from spaceship.forms import (
  Register, Login, AcceptInvitation, DeclineInvitation, CreateCrew, DietSurvey
)

logger = logging.getLogger('spaceship.views')


@app.route('/register', methods=['GET', 'POST'])
def register():
  """Registers a new user; if already exists, logs them in"""
  oauth_user_info = session.pop('oauth_user_info', None)
  register = Register()
  user = None

  try:
    # did we authenticate via oauth?
    if oauth_user_info:
      user = login_or_register.register(oauth_user_info=oauth_user_info, as_captain=True)

    # did the user submit a registration form?
    elif register.validate_on_submit():
      user = login_or_register.register(
        email=register.data['email'], name=register.data['name'], password=register.data['password'], as_captain=True)

  # user already exists, but we provided a different password or something...
  except login_or_register.LoginFailed:
    flash({'msg': 'Email address already registered; pick another, or click Log In', 'level': 'danger'})

  # successfully registered
  if user:
    login_user(user)
    return redirect_for_logged_in()

  # didn't work out? return them to registration page
  session['oauth_next_url'] = url_for('register')
  return render_template('register.html', register=register)

@app.route('/confirm_email/<token>', methods=['GET'])
@login_required
def confirm_email(token):
  try:
    email_from_token = confirm_token(token)
  except:
    email_from_token = None

  if email_from_token == current_user.email:
    user = User.query.filter(User.email == current_user.email).first()
    user.email_confirmed = True
    user.save()
    flash({'msg':'Email address confirmed', 'level': 'success'})
  else:
    flash({'msg':'Invalid email token; email address not confirmed', 'level': 'danger'})

  return redirect(url_for('dashboard'))


def redirect_for_logged_in():
  return redirect(url_for('dashboard'))

@app.route('/')
def home():
  if current_user.is_authenticated:
    return redirect_for_logged_in()

  return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect_for_logged_in()

  oauth_user_info = session.pop('oauth_user_info', None)
  login = Login()
  user = None

  # try to log in
  try:
    if oauth_user_info:
      user = login_or_register.login(oauth_user_info=oauth_user_info)
    elif login.validate_on_submit():
      user = login_or_register.login(email=login.data['email'], password=login.data['password'])
  except login_or_register.LoginFailed:
    flash({'msg':'Incorrect email or password. Try again?', 'level':'danger'})

  # logged in successfully; send them where they were trying to go
  if user:
    login_user(user)

    try:
      next_url = request.values['next']

      # make sure the next url is valid
      parsed_next_url = urlparse(next_url)
      if parsed_next_url.netloc:
        raise ValueError('only relative redirect allowed')

      return redirect(next_url)
    except:
      return redirect_for_logged_in()

  # if we got here, no login; render login page
  session['oauth_next_url'] = url_for('login')
  return render_template('login.html', login=login)

@app.route('/enlist/<key>', methods=['GET', 'POST'])
def accept_invitation(key):
  invitation: Invitation = Invitation.query.filter(Invitation.key_for_sharing == key).first()
  if not invitation:
    flash({'msg':f'Could not find invitation', 'level':'danger'})
    return redirect(url_for('home'))

  accept = AcceptInvitation()
  register = Register()

  # the user logged in already; they can only accept the invitation
  if current_user.is_authenticated:
    if accept.validate_on_submit():
      team = join_team(invitation, current_user)
      flash({'msg':f'Welcome to team {team.name}, {current_user.name}!', 'level':'success'})
      return redirect(url_for('dashboard'))

  # not logged in -- they must be registering
  else:
    user = None

    oauth_user_info = session.pop('oauth_user_info', None)
    if oauth_user_info:
      user = login_or_register(oauth_user_info=oauth_user_info)

    elif register.validate_on_submit():
      try:
        user = login_or_register.register(
          email=register.data['email'], name=register.data['name'], password=register.data['password'])
      except login_or_register.LoginFailed:
        flash({'msg': 'Email address is already registered; pick another, or log in first', 'level': 'danger'})

    # successfully registered; accept the invite
    if user:
      team = join_team(invitation, user)
      flash({'msg':f'Welcome to team {team.name}, {user.name}!', 'level':'success'})

      login_user(user)
      return redirect(url_for('dashboard'))

  # if we got here, we haven't yet accepted an invitiation; we need to render the page

  # figure out the email to auto-populate into a registration form
  invited_email = invitation.invited_email
  if invitation.already_accepted:
    invited_email = None

  # logged-in users can only accept an invite
  if current_user.is_authenticated:
    register = None
    if current_user.email != invited_email:
      flash({
        'msg':f'Invitation was for {invited_email} but you are logged in as {current_user.email}',
        'level':'warning'
      })

  # non-logged-in users get a registration form, possibly with a pre-filled email address
  else:
    accept = None
    if invited_email and not register.data['email']:
      register.data['email'] = invited_email

  team = Team.query.get(invitation.team_id)
  crew = team.members if team else []

  session['oauth_next_url'] = url_for('accept_invitation', key=invitation.key_for_sharing)
  return render_template(
    'enlist.html',
    invitation=invitation,
    register=register,
    accept=accept,
  )

@app.route('/logout')
def logout():
  logout_user()
  flash({'msg':'Logged out successfully', 'level':'success'})
  return redirect(url_for('home'))
