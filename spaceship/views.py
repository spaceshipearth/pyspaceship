
from itsdangerous import URLSafeTimedSerializer
from flask import render_template, flash, redirect, url_for, jsonify, request, session
from flask_login import login_user, logout_user, login_required, current_user
from peewee import DatabaseError, IntegrityError, fn
from urllib.parse import urlparse

from . import app
from . import email
from . import names
from . import achievements

from .db import db
from .models.user import User
from .models.team import Team
from .models.team_user import TeamUser
from .models.invitation import Invitation
from .models.goal import Goal
from .models.mission import Mission
from .models.mission_goal import MissionGoal
from .models.pledge import Pledge
from .forms.register import Register
from .forms.create_mission import CreateMissionForm
from .forms.login import Login
from .forms.invite import Invite
from .forms.enlist import AcceptInvitation, DeclineInvitation
from .forms.create_crew import CreateCrew

import json
import hashlib
import logging
import pendulum
import uuid

logger = logging.getLogger('views')

def teams(user):
  return (Team
          .select()
          .join(TeamUser)
          .join(User)
          .where(User.id == user.id))

def get_team_if_member(team_id):
  try:
    team = Team.get(Team.id == team_id)
  except Team.DoesNotExist:
    return None
  if not any(t.id == int(team_id) for t in set(teams(current_user))):
    return None
  return team

def redirect_for_logged_in():
  # take the user directly to their team if they only have one, dashboard otherwise
  current_user_teams = teams(current_user)
  if len(current_user_teams) > 1:
    return redirect(url_for('dashboard'))
  return redirect(url_for('crew', team_id=current_user_teams[0].id))

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
    try:
      user = User.get(User.email == email_address)
    except User.DoesNotExist:
      user = None
    else:
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
  current_user_teams = teams(current_user)
  return render_template('dashboard.html',
                         teams=current_user_teams,
                         missions=Mission.select(),
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

@app.route('/crew/<team_id>/create-mission', methods=['GET', 'POST'])
@login_required
def create_mission(team_id):
  create_mission_form = CreateMissionForm(team_id=team_id)
  if create_mission_form.validate_on_submit():
    with db.atomic() as transaction:
      try:
        mission = Mission(title="Plant based diet", 
                          short_description="Save the planet by eating more plants",
                          duration_in_weeks=1,
                          started_at=create_mission_form.data['start'],
                          team_id=team_id)
        mission.save()    
        goal = Goal(short_description=create_mission_form.data['goal'],
                    category='diet')
        goal.save()
        missiongoal = MissionGoal( 
          mission=mission.id,
          goal=goal.id,
          week=1)
        missiongoal.save()
      except (IntegrityError, DatabaseError) as e:
        transaction.rollback()
        logger.exception(e)
        flash({'msg':f'Error creating mission'})
        return redirect(url_for('dashboard'))

    return redirect(url_for('dashboard'))
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
    with db.atomic() as transaction:
      try:
        u = User(name=name, email=email_address, email_confirmed=email_confirmed)
        if password:
          u.set_password(password)
        u.save()

        t = Team(captain=u, name=names.name_team())
        t.save()
        tu = TeamUser(team=t, user=u)
        tu.save()
      except IntegrityError:
        transaction.rollback()
        # don't automatically log in existing oauth users because we want login to trigger a password reset
        flash({'msg':f'Email already registered. Please sign-in'})
        return redirect(url_for('login'))
      except DatabaseError as e:
        # TODO: docs mention ErrorSavingData but I cannot find wtf they are talking about
        transaction.rollback()
        flash({'msg':f'Error registering', 'level':'danger'})
        logger.exception(e)
        return redirect(url_for('home'))

    login_user(u)

    achievements.become_captain(u)

    if not email_confirmed:
      token = generate_confirmation_token(email_address)
      email.send(to_emails=email_address,
          subject='Please verify you email for Spaceship Earth',
          html_content=render_template('confirm_email.html',
          confirmation_url=url_for('confirm_email', token=token, _external=True)))

    return redirect_for_logged_in()

  session['oauth_next_url'] = url_for('register')
  return render_template('register.html', register=register)

@app.route('/confirm_email/<token>', methods=['GET'])
@login_required
def confirm_email(token):
  if confirm_token(token) == current_user.email:
    user = (User
                .select()
                .where(User.email == current_user.email)
                .get())
    user.email_confirmed = True
    user.save()
  return redirect(url_for('dashboard'))

@app.route('/create_crew', methods=['POST'])
@login_required
def create_crew():
  create_crew = CreateCrew()
  if create_crew.validate_on_submit():
    with db.atomic() as transaction:
      try:
        u = current_user.id
        t = Team(captain=u, name=names.name_team())
        t.save()
        tu = TeamUser(team=t, user=u)
        tu.save()
        achievements.become_captain(current_user)
      except (IntegrityError, DatabaseError) as e:
        transaction.rollback()
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
  team_size = TeamUser.select(fn.COUNT(TeamUser.user_id)).where(TeamUser.team_id == team_id).scalar()

  invite = Invite()
  if is_captain and invite.validate_on_submit():
    message = invite.data['message']
    emails = invite.data['emails'].split()
    with db.atomic() as transaction:
      try:
        for invited_email in emails:
          key_for_sharing = uuid.uuid4()
          iv = Invitation(inviter_id=current_user.id,
                          key_for_sharing=key_for_sharing,
                          team_id=team_id,
                          invited_email=invited_email,
                          message=message,
                          status='sent')
          iv.save()
          # TODO probably should queue this instead
          email.send(to_emails=invited_email,
              subject='Invitation to join',
              html_content=render_template('invite_email.html', inviter=current_user.name, message=message, key_for_sharing=key_for_sharing))
        achievements.invite_crew(current_user)
      except DatabaseError:
        transaction.rollback()
        flash({'msg':f'Error sending invitations', 'level':'danger'})
      else:
        flash({'msg':'Invitations are on the way!', 'level':'success'})
    return redirect(url_for('crew', team_id=team_id), code=303)

  crew = (User
            .select()
            .join(TeamUser)
            .join(Team)
            .where(Team.id == team_id))
  invitations = (Invitation
                 .select()
                 .where(Invitation.team_id == team_id))

  return render_template('crew.html',
                         is_captain=is_captain,
                         team=team,
                         team_size=team_size,
                         missions=Mission.select(),
                         crew=crew,
                         invitations=invitations,
                         invite=invite,
                         achievements=achievements.for_team(team))

@app.route('/enlist/<key>', methods=['GET', 'POST'])
def enlist(key):
  try:
    invitation = (Invitation
                  .select()
                  .where(Invitation.key_for_sharing == key)
                  .get())
  except Invitation.DoesNotExist:
    invitation = None
  if not invitation:
    flash({'msg':f'Could not find invitation', 'level':'danger'})
    return redirect(url_for('home'))
  if invitation.status == 'accepted':
    flash({'msg':f'Invitation was already accepted.', 'level':'danger'})
    return redirect(url_for('home'))

  decline = DeclineInvitation()
  if decline.decline.data and decline.validate():
    with db.atomic() as transaction:
      try:
        invitation.status = 'declined'
        invitation.save()
      except DatabaseError:
        transaction.rollback()
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
  elif User.select().where(User.email == invitation.invited_email):
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
    with db.atomic() as transaction:
      try:
        u = User(name=name, email=email_address, email_confirmed=True)
        if password:
          u.set_password(password)
        u.save()
        accept_invitation(invitation, u)
      except IntegrityError:
        transaction.rollback()
        flash({'msg':f'Email already registered. Please sign-in', 'level': 'danger'})
        return redirect(url_for('login'))
      except DatabaseError:
        transaction.rollback()
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

  crew = (User
            .select()
            .join(TeamUser)
            .join(Team)
            .where(Team.id == invitation.team_id))

  session['oauth_next_url'] = url_for('enlist', key=invitation.key_for_sharing)
  return render_template('enlist.html', invitation=invitation, accept=AcceptInvitation(), decline=decline, register=register, crew=crew)

@app.route('/rsvp/<key>/<status>', methods=['POST'])
@login_required
def rsvp(key, status):
  try:
    invitation = (Invitation
                  .select()
                  .where(Invitation.key_for_sharing == key)
                  .get())
  except Invitation.DoesNotExist:
    invitation = None
  if not invitation:
    flash({'msg':f'Could not find invitation', 'level':'danger'})
    return redirect(url_for('home'))
  if invitation.status == 'accepted':
    flash({'msg':f'Invitation was already accepted.', 'level':'danger'})
    return redirect(url_for('home'))

  with db.atomic() as transaction:
    try:
      if status == 'accepted':
        accept_invitation(invitation, User.get(User.id == current_user.id))
      elif status == 'declined':
        invitation.status = 'declined'
        invitation.save()
      else:
        raise ValueError(f'Invalid rsvp {status}')
    except DatabaseError:
      transaction.rollback()
      flash({'msg':f'Database error', 'level':'danger'})
    except ValueError as err:
      flash({'msg':f'{str(err)}', 'level':'danger'})
      return redirect(url_for('home'))
    else:
      flash({'msg':f'Invitation {status}', 'level':'success'})
      return redirect(url_for('home'))

  return redirect(url_for('home'))

def accept_invitation(invitation, user):
  already_on_team = (TeamUser
      .select()
      .where((TeamUser.user_id == user.id) &
             (TeamUser.team_id == invitation.team)))
  if already_on_team:
    raise ValueError('Already on team')

  tu = TeamUser(team=invitation.team, user=user)
  tu.save()
  invitation.status = 'accepted'
  invitation.save()

  # tell captain about new user
  captain = (User
                .select()
                .join(Team, on=(Team.captain == User.id))
                .where(Team.id == invitation.team)
                .get())
  email.send(to_emails=captain.email,
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
  try:
    user = User.get(User.id == user_id)
  except User.DoesNotExist:
    return redirect(url_for('dashboard'))

  is_me = current_user.id == int(user_id)
  if not is_me and not (set(teams(current_user)) & set(teams(user))):
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
    try:
      team = Team.get(Team.id == object_id)
    except Team.DoesNotExist:
      return jsonify({'ok': False})
    if current_user.id != team.captain.id:
      return jsonify({'ok': False})
    with db.atomic() as transaction:
      try:
        if field_name == 'name':
          team.name = value
          team.save()
        elif field_name == 'description':
          team.description = value
          team.save()
      except DatabaseError:
        transaction.rollback()
        return jsonify({'ok': False})
      else:
        return jsonify({'ok': True})

  elif table_name == 'user':
    try:
      user = User.get(User.id == object_id)
    except User.DoesNotExist:
      return jsonify({'ok': False})
    if current_user.id != user.id:
      return jsonify({'ok': False})
    with db.atomic() as transaction:
      try:
        if field_name == 'name':
          user.name = value
          user.save()
        #elif field_name == 'email':
        #  user.email = value
        #  user.save()
      except DatabaseError:
        transaction.rollback()
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
