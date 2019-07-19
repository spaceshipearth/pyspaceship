
import hashlib
import logging
import pendulum

from itsdangerous import URLSafeTimedSerializer
from flask import render_template, flash, redirect, url_for, jsonify, request, session
from flask_login import login_user, logout_user, login_required, current_user

from sqlalchemy.exc import DatabaseError, IntegrityError
from urllib.parse import urlparse

from spaceship import app, email, names, achievements
from spaceship.db import db
from spaceship.models import User, Team, TeamUser, Invitation, Goal, Mission
from spaceship.forms import (
  Register, CreateMissionForm, Login, AcceptInvitation, DeclineInvitation, CreateCrew
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

  email_address = None
  password = None
  if oauth_user_info:
    email_address = oauth_user_info.get('email')
  elif login.validate_on_submit():
    email_address = login.data['email']
    password = login.data['password']

  if email_address:
    user = User.query.filter(User.email == email_address).first()

    if user:
      if oauth_user_info:
        # clear password in case someone else claimed this email
        user.password_hash = None
        user.save()
      elif not user.password_hash:
        # user's password was previously cleared
        # TODO redirect to password reset flow
        user = None
      elif not user.check_password(password):
        user = None

    if user:
      login_user(user)
      try:
        next_url = request.values['next']
        parsed_next_url = urlparse(next_url)
        if parsed_next_url.netloc:
          raise ValueError('only relative redirect allowed')
        return redirect(next_url)
      except:
        return redirect_for_logged_in()

    else:
      flash({'msg':'Incorrect email or password. Try again?', 'level':'danger'})

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


def generate_confirmation_token(email):
    """Confirmation email token."""
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['EMAIL_CONFIRM_SALT'])

def confirm_token(token, expiration=3600):
    """Plausibility check of confirmation token."""
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=app.config['EMAIL_CONFIRM_SALT'], max_age=expiration)
    except:
        return False
    return email

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
  print (goals[0].short_description)
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
  oauth_user_info = session.pop('oauth_user_info', None)
  register = Register()

  name = None
  email_address = None
  email_confirmed = False
  password = None
  if oauth_user_info:
    name = oauth_user_info.get('name')
    email_address = oauth_user_info.get('email')
    email_confirmed = True
  elif register.validate_on_submit():
    name = register.data['name']
    email_address = register.data['email']
    password = register.data['password']

  if name and email_address:
    try:
      u = User(name=name, email=email_address, email_confirmed=email_confirmed)
      if password:
        u.set_password(password)
      u.save()

      t = Team(captain=u, name=names.name_team())
      t.save()
      tu = TeamUser(team=t, user=u)
      tu.save()
    except IntegrityError as e:
      logger.exception(e)
      db.session.rollback()
      # don't automatically log in existing oauth users because we want login to trigger a password reset
      flash({'msg':f'Email already registered. Please sign-in'})
      return redirect(url_for('login'))
    except DatabaseError as e:
      db.session.rollback()
      flash({'msg':f'Error registering', 'level':'danger'})
      logger.exception(e)
      return redirect(url_for('home'))

    login_user(u)

    achievements.become_captain(u)

    if not email_confirmed:
      token = generate_confirmation_token(email_address)
      email.send.delay(to_emails=email_address,
          subject='Please verify your email for Spaceship Earth',
          html_content=render_template('confirm_email.html',
          confirmation_url=url_for('confirm_email', token=token, _external=True)))

    return redirect_for_logged_in()

  session['oauth_next_url'] = url_for('register')
  return render_template('register.html', register=register)

@app.route('/confirm_email/<token>', methods=['GET'])
@login_required
def confirm_email(token):
  if confirm_token(token) == current_user.email:
    user = User.query.filter(User.email == current_user.email).first()
    user.email_confirmed = True
    user.save()
  return redirect(url_for('dashboard'))

@app.route('/create_crew', methods=['POST'])
@login_required
def create_crew():
  create_crew = CreateCrew()
  if create_crew.validate_on_submit():
    try:
      t = Team(
        captain=current_user,
        name=names.name_team())
      t.members.append(current_user)
      t.save()
      achievements.become_captain(current_user)
    except (IntegrityError, DatabaseError) as e:
      db.session.rollback()
      flash({'msg':f'Error creating a new crew', 'level':'danger'})

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

  upcoming_missions = [mission for mission in team.missions if mission.is_upcoming]
  running_missions = [mission for mission in team.missions if mission.is_running]
  completed_missions = [mission for mission in team.missions if mission.is_over]

  return render_template('crew.html',
                         is_captain=is_captain,
                         team=team,
                         team_size=team_size,
                         completed_missions=completed_missions,
                         running_missions=running_missions,
                         upcoming_missions=upcoming_missions,
                         captain=team.captain,
                         crew=list(filter(lambda x: x.id != team.captain.id,team.members)),
                         invite=invite,
                         achievements=achievements.for_team(team))

@app.route('/invite/<team_id>', methods=['POST'])
def invite(team_id):
  if not current_user:
    return jsonify({'error': 'Must be logged in.'})
  team = get_team_if_member(team_id)
  if not team:
    return jsonify({'error': 'Must be a member of team.'})

  subject = request.form.get('subject', '')
  if not subject:
    return jsonify({'error': 'Subject cannot be blank.'})
  message = request.form.get('message', '')
  # quilljs needs <p><br></p> to show line breaks even though everything is in a paragraph
  # this creates extra line breaks in gmail so just strip it out
  message = message.replace('<p><br></p>', '')
  emails = request.form.get('emails', '').split()
  if not emails:
    return jsonify({'error': 'Need at least one email in To: line.'})
  try:
    for invited_email in emails:
      iv = Invitation(
        inviter_id=current_user.id,
        team_id=team_id,
        invited_email=invited_email,
        message=message,
        status='sent')
      iv.save()

      # each recipient sees a unique invite link
      invite_url = url_for('enlist', key=iv.key_for_sharing, _external=True)
      if 'href="join"' in message:
        html_content = message.replace('href="join"', f'href="{invite_url}"')
      else:
        # if the user deleted the invite link, put it at the bottom
        html_content = f'{message}<p><a href="{invite_url}">Click here to join</a>'

      email.send.delay(
        to_emails=invited_email,
        subject=subject,
        html_content=html_content,
      )

    achievements.invite_crew(current_user)
  except:
    return jsonify({'error': 'Error sending invitations.'})

  return jsonify({'ok': True})

@app.route('/enlist/<key>', methods=['GET', 'POST'])
def enlist(key):
  invitation = Invitation.query.filter(Invitation.key_for_sharing == key).first()
  if not invitation:
    flash({'msg':f'Could not find invitation', 'level':'danger'})
    return redirect(url_for('home'))
  if invitation.status == 'accepted':
    flash({'msg':f'Invitation was already accepted.', 'level':'danger'})
    return redirect(url_for('home'))

  decline = DeclineInvitation()
  if decline.decline.data and decline.validate():
    try:
      invitation.status = 'declined'
      invitation.save()
    except DatabaseError:
      db.session.rollback()
      flash({'msg':f'Database error', 'level':'danger'})
    else:
      flash({'msg':f'Invitation declined', 'level':'success'})

    return redirect(url_for('home'))

  oauth_user_info = session.pop('oauth_user_info', None)
  register = None

  if current_user.is_authenticated:
    email_mismatch = (invitation.invited_email and current_user.email != invitation.invited_email)
    if email_mismatch:
      # could have gotten the invite via an alias? but also maybe multiple accounts. let them decide
      flash({'msg':f'Invitation was for ' + invitation.invited_email + ' but you are logged in as ' + current_user.email, 'level':'warning'})
  elif User.query.filter(User.email == invitation.invited_email).count():
    # assume cookies were cleared
    flash({'msg':f'Please log in as ' + invitation.invited_email, 'level':'warning'})
    return redirect(url_for('login', next=url_for('enlist', key=key)))
  else:
    register = Register()
    if not register.is_submitted():
      # auto populate the email from the invitation but allow the user to change it
      register.email.process_data(invitation.invited_email)

  name = None
  email_address = None
  password = None
  if oauth_user_info:
    name = oauth_user_info.get('name')
    email_address = oauth_user_info.get('email')
  elif register and register.validate_on_submit():
    name = register.data['name']
    email_address = register.data['email']
    password = register.data['password']

  if name and email_address:
    try:
      u = User(name=name, email=email_address, email_confirmed=True)
      if password:
        u.set_password(password)
      u.save()
      accept_invitation(invitation, u)
    except IntegrityError:
      db.session.rollback()
      flash({'msg':f'Email already registered. Please sign-in', 'level': 'danger'})
      return redirect(url_for('login'))
    except DatabaseError:
      db.session.rollback()
      flash({'msg':f'Database error', 'level':'danger'})
      return redirect(url_for('home'))
    except ValueError as err:
      flash({'msg':f'{str(err)}', 'level':'danger'})
      return redirect(url_for('home'))
    else:
      if not current_user.is_authenticated:
        login_user(u)
      return redirect_for_logged_in()
    return redirect(url_for('dashboard'))

  team = Team.query.get(invitation.team_id)
  crew = team.members if team else []

  session['oauth_next_url'] = url_for('enlist', key=invitation.key_for_sharing)
  return render_template('enlist.html', invitation=invitation, accept=AcceptInvitation(), decline=decline, register=register, crew=crew)

@app.route('/rsvp/<key>/<status>', methods=['POST'])
@login_required
def rsvp(key, status):
  invitation = Invitation.query.filter(Invitation.key_for_sharing == key).first()
  if not invitation:
    flash({'msg':f'Could not find invitation', 'level': 'danger'})
    return redirect(url_for('home'))
  if invitation.status == 'accepted':
    flash({'msg':f'Invitation was already accepted.', 'level': 'danger'})
    return redirect(url_for('home'))

  try:
    if status == 'accepted':
      accept_invitation(invitation, current_user)
    elif status == 'declined':
      invitation.status = 'declined'
      invitation.save()
    else:
      raise ValueError(f'Invalid rsvp {status}')
  except DatabaseError:
    db.session.rollback()
    flash({'msg':f'Database error', 'level':'danger'})
  except ValueError as err:
    flash({'msg':f'{str(err)}', 'level':'danger'})
    return redirect(url_for('home'))
  else:
    flash({'msg':f'Invitation {status}', 'level':'success'})
    return redirect(url_for('home'))

  return redirect(url_for('home'))

def accept_invitation(invitation, user):
  already_on_team = (TeamUser.query.filter(
      (TeamUser.user_id == user.id) &
      (TeamUser.team_id == invitation.team_id))).count()
  if already_on_team:
    raise ValueError('Already on team')

  tu = TeamUser(team=invitation.team, user=user)
  tu.save()
  invitation.status = 'accepted'
  invitation.save()

  # tell captain about new user
  team = Team.query.get(invitation.team_id)
  if not team:
    return

  captain = team.captain
  email.send.delay(
    to_emails=[captain.email],
    subject='Your crew is growing!',
    html_content=render_template('crew_growing_email.html',
      team_id=invitation.team,
      name=user.name, _external=True))

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
