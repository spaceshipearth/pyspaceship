
import hashlib
import logging
import pendulum

from flask import render_template, flash, redirect, url_for, jsonify, request, session
from flask_login import login_user, logout_user, login_required, current_user

from sqlalchemy.exc import DatabaseError, IntegrityError
from urllib.parse import urlparse

from spaceship import app, email, achievements, team_invite, login_or_register
from spaceship.accept_invitation import accept_invitation
from spaceship.create_team import create_team
from spaceship.confirm_email import confirm_token
from spaceship.db import db
from spaceship.models import User, Team, Invitation, Goal, Mission
from spaceship.forms import (
  Register, CreateMissionForm, Login, AcceptInvitation, CreateCrew
)

logger = logging.getLogger('spaceship.views')

def get_team_if_member(team_id):
  team = Team.query.get(team_id)
  if not team:
    return None

  if team not in current_user.teams:
    return None

  return team

def redirect_for_logged_in():
  # take the user directly to their team if they only have one, dashboard otherwise
  if len(current_user.teams) != 1:
    return redirect(url_for('dashboard'))
  return redirect(url_for('crew', team_id=current_user.teams[0].id))

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

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/contact')
def contact():
  return render_template('contact.html')

@app.route('/dashboard')
@login_required
def dashboard():
  # to avoid redirect loops, this view does not redirect
  return render_template('dashboard.html',
                         teams=current_user.teams,
                         missions=Mission.query.all(),
                         create_crew=CreateCrew())

@app.route('/mission/<mission_id>/cancel', methods=['POST'])
@login_required
def cancel_mission_ajax(mission_id):
  mission = Mission.query.filter(Mission.id == mission_id).first()
  if not mission:
    return jsonify({'error': 'Could not find mission'})

  if mission.team.captain != current_user:
    return jsonify({'error': 'Only captains can cancel missions'})

  if mission.is_deleted:
    return jsonify({'error': 'Mission was already cancelled'})

  try:
    mission.deleted_at = pendulum.now('UTC')
    mission.save()
  except DatabaseError as e:
    logger.exception(e)
    return jsonify({'error': 'Failed to cancel mission'})

  return jsonify({'ok': True})

@app.route('/crew/<team_id>/create-mission', methods=['GET', 'POST'])
@login_required
def create_mission(team_id):
  goals = list(Goal.query.filter())
  create_mission_form = CreateMissionForm(team_id=team_id, goals=goals)
  if create_mission_form.validate_on_submit():
    try:
      goal_id = create_mission_form.data['goal']
      goal = Goal.query.get(goal_id)

      mission = Mission(
        title="Plant based diet",
        short_description="Save the planet by eating more plants",
        duration_in_weeks=1,
        started_at=create_mission_form.data['start'],
        team_id=team_id,
      )

      mission.goals.append(goal)
      mission.save()

    except (IntegrityError, DatabaseError) as e:
      db.session.rollback()
      logger.exception(e)
      flash({'msg':f'Error creating mission'})
      return redirect(url_for('crew', team_id=team_id))

    # schedule emails
    email.schedule_mission_emails(mission)
    return redirect(url_for('crew', team_id=team_id))

  return render_template('create_mission.html', create_mission_form=create_mission_form)

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

@app.route('/create_crew', methods=['POST'])
@login_required
def create_crew():
  create_crew = CreateCrew()
  if create_crew.validate_on_submit():
    create_team(current_user)

  return redirect(url_for('dashboard'))

@app.route('/crew/<team_id>', methods=['GET', 'POST'])
@login_required
def crew(team_id):
  team = get_team_if_member(team_id)
  if not team:
    flash({'msg': 'Could not find team', 'level': 'danger'})
    return redirect(url_for('dashboard'))

  is_captain = team.captain_id == current_user.id
  team_size = len(team.members)
  generic_invite = team.generic_invitation_from(current_user)

  return render_template(
    'crew.html',
    is_captain=is_captain,
    team=team,
    team_size=team_size,
    completed_missions=[mission for mission in team.missions if mission.is_over],
    running_missions=[mission for mission in team.missions if mission.is_running],
    upcoming_missions=[mission for mission in team.missions if mission.is_upcoming],
    crew=list(filter(lambda x: x.id != team.captain.id,team.members)),
    achievements=achievements.for_team(team),
    invitation_subject=team_invite.DEFAULT_SUBJECT,
    invitation_message=team_invite.default_message(current_user, team),
    invite_link=url_for('accept_invitation', key=generic_invite.key_for_sharing, _external=True),
  )

@app.route('/invite/<team_id>', methods=['POST'])
def invite(team_id):
  if not current_user:
    return jsonify({'error': 'Must be logged in.'})

  error = team_invite.send(
    inviter=current_user,
    team_id=team_id,
    subject=request.form.get('subject'),
    message=request.form.get('message'),
    emails=request.form.get('emails'),
  )

  if error is None:
    return jsonify({'ok': True})
  else:
    return jsonify({'error': error})

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
      team = accept_invitation(invitation, current_user)
      flash({'msg':f'Welcome to team {team.name}, {current_user.name}!', 'level':'success'})
      return redirect(url_for('crew', team_id=team.id))

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
      team = accept_invitation(invitation, user)
      flash({'msg':f'Welcome to team {team.name}, {user.name}!', 'level':'success'})

      login_user(user)
      return redirect(url_for('crew', team_id=team.id))

  # if we got here, we haven't yet accepted an invitiation; we need to render the page
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

@app.route('/profile/<user_id>')
@login_required
def profile(user_id):
  user = User.query.filter(User.id == user_id).first()
  if user is None:
    return redirect(url_for('dashboard'))

  is_me = current_user.id == int(user_id)
  if not is_me and not (set(current_user.teams) & set(user.teams)):
    # only allow looking at own and teammates' profiles to prevent enumerating users
    return redirect(url_for('dashboard'))

  return render_template('profile.html',
                         can_edit=is_me,
                         user=user,
                         achievements=achievements.for_user(user))

@app.route('/edit', methods=['POST'])
def edit():
  if not current_user.is_authenticated:
    return jsonify({'ok': False})

  table_name = request.form['table']
  try:
    object_id = int(request.form['id'])
  except ValueError:
    return jsonify({'ok': False})
  field_name = request.form['field']
  value = request.form['value']

  if table_name == 'team':
    team = Team.query.filter(Team.id == object_id).first()
    if team is None:
      return jsonify({'ok': False})
    if current_user.id != team.captain.id:
      return jsonify({'ok': False})
    try:
      if field_name == 'name':
        team.name = value
        team.save()
      elif field_name == 'description':
        team.description = value
        team.save()
    except DatabaseError:
      db.session.rollback()
      return jsonify({'ok': False})
    else:
      return jsonify({'ok': True})

  elif table_name == 'user':
    user = User.query.filter(User.id == object_id).first()
    if user is None:
      return jsonify({'ok': False})
    if current_user.id != user.id:
      return jsonify({'ok': False})
    try:
      if field_name == 'name':
        user.name = value
        user.save()
      #elif field_name == 'email':
      #  user.email = value
      #  user.save()
    except DatabaseError:
      db.session.rollback()
      return jsonify({'ok': False})
    else:
      return jsonify({'ok': True})

  return jsonify({'ok': False})

@app.context_processor
def gravatar():
  def write_gravatar_link(email, size=100, default='robohash'):
    url = 'https://www.gravatar.com/avatar/'
    hash_email = hashlib.md5(email.encode('ascii')).hexdigest()
    link = "{url}{hash_email}?s={size}&d={default}".format(url=url, hash_email=hash_email, size=size, default=default)
    return link
  return dict(gravatar=write_gravatar_link)

@app.before_request
def cleanup_oauth_session_fields():
  if request.path.startswith('/static'):
    return
  if request.path not in ('/google/login', '/google/auth'):
    session.pop('oauth_next_url', None)
  if request.path not in ('/login', '/register') and not request.path.startswith('/enlist'):
    session.pop('oauth_user_info', None)

@app.before_request
def mock_time():
  try:
    fake_time = request.values.get('now')
    now = pendulum.parse(fake_time)
    pendulum.set_test_now(now)
  except:
    pass

#@app.before_request
#def debug_oauth_fields():
#  import sys
#  print(f'oauth_next_url={session.get("oauth_next_url", "")}', file=sys.stderr)
#  print(f'oauth_user_info={session.get("oauth_user_info", "")}', file=sys.stderr)

@app.teardown_request
def unmock_time(response):
  pendulum.set_test_now()

@app.route('/health')
def health():
  return jsonify({'OK': True})
