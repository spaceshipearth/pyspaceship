
from flask import render_template, flash, redirect, url_for, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from peewee import DatabaseError, IntegrityError, fn

from . import app
from . import email
from . import names

from .db import db
from .models.user import User
from .models.team import Team
from .models.team_user import TeamUser
from .models.invitation import Invitation
from .models.goal import Goal
from .models.mission import Mission
from .models.pledge import Pledge
from .forms.register import Register
from .forms.login import Login
from .forms.invite import Invite
from .forms.enlist import EnlistExistingUser, EnlistNewUser
from .forms.start_mission import StartMission

import hashlib
import pendulum
import uuid

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

@app.route('/')
def home():
  # take the user directly to their team if they only have one, dashboard otherwise
  if current_user.is_authenticated:
    current_user_teams = teams(current_user)
    if len(current_user_teams) > 1:
      return redirect(url_for('dashboard'))
    else:
      return redirect(url_for('roster', team_id=current_user_teams[0].id))

  return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('dashboard'))

  login = Login()
  if login.validate_on_submit():
    try:
      user = User.get(User.email == login.data['email'])
    except User.DoesNotExist:
      user = None
    else:
      if not user.check_password(login.data['password']):
        user = None

    if user:
      login_user(user)
      flash({'msg':'Access Granted', 'level':'success'})
      try:
        return redirect(url_for(request.values.get('next')))
      except:
        return redirect(url_for('dashboard'))

    else:
      flash({'msg':'Incorrect email or password. Try again?', 'level':'danger'})

  return render_template('login.html', login=login)

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/mission/<team_id>/<mission_id>', methods=['GET', 'POST'])
@login_required
def mission(team_id, mission_id):
  try:
    mission = Mission.get(Mission.id == mission_id)
  except DoesNotExist:
    flash({'msg': 'Could not find mission', 'level': 'danger'})
    return redirect(url_for('dashboard'))

  team = get_team_if_member(team_id)
  if not team:
    flash({'msg': 'Could not find team', 'level': 'danger'})
    return redirect(url_for('dashboard'))
  is_captain = team.captain_id == current_user.id

  start_mission = StartMission()
  if start_mission.validate_on_submit():
    if is_captain and not team.mission:
      with db.atomic() as transaction:
        try:
          team.mission = mission
          team.mission_start_at = pendulum.now()
          team.save()
        except IntegrityError:
          transaction.rollback()
          flash({'msg': f'Database error', 'level': 'danger'})
        except DatabaseError:
          transaction.rollback()
          flash({'msg': f'Database error', 'level': 'danger'})
        else:
          flash({'msg': f'Started mission!', 'level': 'success'})
    else:
      flash({'msg': 'Could not start mission', 'level': 'danger'})

  week_of_mission = 0
  mission_pledges = []
  if team.mission and team.mission.id == mission.id:
    week_of_mission = (pendulum.now() - team.mission_start_at).in_weeks() + 1
    if week_of_mission >= 5:
      with db.atomic() as transaction:
        try:
          team.mission = None
          team.save()
          # TODO roll up to completed missions
        except IntegrityError:
          transaction.rollback()
        except DatabaseError:
          transaction.rollback()
        else:
          flash({'msg': f'Mission has concluded.', 'level': 'success'})
    else:
      mission_end_at = team.mission_start_at.add(weeks=4)
      mission_pledges = (Pledge.select()
        .join(TeamUser, on=(Pledge.user_id == TeamUser.user_id))
        .where((TeamUser.team_id == team.id) &
               (~((Pledge.start_at > mission_end_at) | (Pledge.end_at < team.mission_start_at)))))
  team_size = TeamUser.select(fn.COUNT(TeamUser.user_id)).where(TeamUser.team_id == team_id).scalar()
  goal_progress = {goal.id: count_goal_progress(team_size=team_size,
                                                pledges=[p for p in mission_pledges if p.goal_id == goal.id])
                   for goal in mission.goals}

  my_pledges = {p.goal_id: p for p in mission_pledges if p.user_id == current_user.id}

  return render_template('mission.html',
                         start_mission=start_mission,
                         week_of_mission=week_of_mission,
                         team=team,
                         is_captain=is_captain,
                         mission=mission,
                         my_pledges=my_pledges,
                         goal_progress=goal_progress)

@app.route('/goal_progress/<team_id>/<goal_id>')
def goal_progress(team_id, goal_id):
  if not current_user.is_authenticated:
    raise ValueError('auth')
  team = get_team_if_member(team_id)
  if not team:
    raise ValueError('auth')
  start_at = pendulum.parse(request.values.get('start_at'))
  mission_end_at = start_at.add(weeks=4)

  mission_pledges_for_goal = (Pledge.select()
    .join(TeamUser, on=(Pledge.user_id == TeamUser.user_id))
    .where((TeamUser.team_id == team.id) &
           (Pledge.goal_id == goal_id) &
           (~((Pledge.start_at > mission_end_at) | (Pledge.end_at < start_at)))))
  team_size = TeamUser.select(fn.COUNT(TeamUser.user_id)).where(TeamUser.team_id == team_id).scalar()
  progress = count_goal_progress(team_size=team_size, pledges=mission_pledges_for_goal)

  my_pledge_id = -1
  for p in mission_pledges_for_goal:
    if p.user_id == current_user.id:
      my_pledge_id = p.id
      break

  return render_template('goal_progress.html', my_pledge_id=my_pledge_id, progress=progress)

def count_goal_progress(team_size=1, pledges=[]):
  progress = {'num_done': 0, 'num_pledged': 0, 'num_active': 0}
  for p in pledges:
    if p.fulfilled:
      progress['num_done'] += 1
    else:
      progress['num_pledged'] += 1
    progress['num_active'] += 1
  def percent_of_team(count):
    return '{:.2f}%'.format(100 * (count / team_size))
  progress['percent_done'] = percent_of_team(progress['num_done'])
  progress['percent_pledged'] = percent_of_team(progress['num_pledged'])
  return progress

@app.route('/pledge', methods=['POST'])
def pledge():
  if not current_user.is_authenticated:
    return jsonify({'ok': False})

  try:
    goal_id = int(request.form['goal_id'])
  except ValueError:
    return jsonify({'ok': False})

  # pledges last for 31 days
  start_at = pendulum.now()
  end_at = start_at.add(days=31)

  # a user can have at most one outstanding pledge for a goal
  conflicting_pledge = (Pledge.select()
      .where((Pledge.user_id == current_user.id) &
             (Pledge.goal_id == goal_id) &
             (start_at < Pledge.end_at)))
  if conflicting_pledge:
    return jsonify({'ok': False, 'conflicting': True})

  try:
    p = Pledge(user_id=current_user.id,
               goal_id=goal_id,
               start_at=start_at,
               end_at=end_at,
               fulfilled=False)
    p.save()
  except IntegrityError:
    return jsonify({'ok': False})
  except DatabaseError:
    return jsonify({'ok': False})
  return jsonify({'ok': True})

@app.route('/dashboard')
@login_required
def dashboard():
  current_user_teams = teams(current_user)

  # go straight to team page iff user only has one team
  if len(current_user_teams) == 1:
    return redirect(url_for('roster', team_id=current_user_teams[0].id))

  return render_template('dashboard.html', teams=current_user_teams, missions=Mission.select())

@app.route('/register', methods=['GET', 'POST'])
def register():
  register = Register()

  if register.validate_on_submit():
    with db.atomic() as transaction:
      try:
        u = User(name=register.data['name'],
                 email=register.data['email'])
        u.set_password(register.data['password'])
        u.save()

        t = Team(captain=u, name=names.name_team())
        t.save()
        tu = TeamUser(team=t, user=u)
        tu.save()
      except IntegrityError:
        transaction.rollback()
        flash({'msg':f'Email already registered. Please sign-in'})
        # TODO: pass-through next?
        return redirect(url_for('login'))
      except DatabaseError:
        # TODO: docs mention ErrorSavingData but I cannot find wtf they are talking about
        transaction.rollback()
        flash({'msg':f'Error registering', 'level':'danger'})
        return redirect(url_for('home'))

    login_user(u)
    flash({'msg':f'Access Granted', 'level':'success'})

    email.send(to_emails=register.data['email'], 
        subject='Please verify you email for Spaceship Earth',
        html_content=render_template('confirm_email.html'))

    return redirect(url_for('dashboard'))

  return render_template('register.html', register=register)


@app.route('/create_crew', methods=['GET'])
def create_crew():
  with db.atomic() as transaction:
    try:
      u = current_user.id
      t = Team(captain=u, name=names.name_team())
      t.save()
      tu = TeamUser(team=t, user=u)
      tu.save()
    except (IntegrityError, DatabaseError) as e:
      transaction.rollback()
      flash({'msg':f'Error creating a new crew', 'level':'danger'})

  return redirect(url_for('dashboard'))




@app.route('/roster/<team_id>', methods=['GET', 'POST'])
@login_required
def roster(team_id):
  team = get_team_if_member(team_id)
  if not team:
    flash({'msg': 'Could not find team', 'level': 'danger'})
    return redirect(url_for('dashboard'))

  is_captain = team.captain_id == current_user.id

  invite = Invite()
  if is_captain and invite.validate_on_submit():
    with db.atomic() as transaction:
      try:
        message = invite.data['message']
        emails = invite.data['emails'].split()
        for email in emails:
          iv = Invitation(inviter_id=current_user.id,
                          key_for_sharing=uuid.uuid4(),
                          team_id=team_id,
                          invited_email=email,
                          message=message,
                          status='pending')
          iv.save()
      except DatabaseError:
        transaction.rollback()
        flash({'msg':f'Error sending invitations', 'level':'danger'})
      else:
        flash({'msg':'Invitations are on the way!', 'level':'success'})

  roster = (User
            .select()
            .join(TeamUser)
            .join(Team)
            .where(Team.id == team_id))
  invitations = (Invitation
                 .select()
                 .where(Invitation.team_id == team_id))

  return render_template('roster.html', is_captain=is_captain, team=team, missions=Mission.select(), roster=roster, invitations=invitations, invite=invite)

@app.route('/enlist/<key>', methods=['GET', 'POST'])
def enlist(key):
  invitation = (Invitation
                .select()
                .where(Invitation.key_for_sharing == key)
                .get())
  if not invitation:
    flash({'msg':f'Could not find invitation', 'level':'danger'})
    return redirect(url_for('home'))
  if invitation.status == 'accepted':
    return redirect(url_for('dashboard'))

  if current_user.is_authenticated:
    enlist = EnlistExistingUser()
    email_mismatch = (invitation.invited_email and current_user.email != invitation.invited_email)
    if not enlist.is_submitted() and email_mismatch:
      # could have gotten the invite via an alias? but also maybe multiple accounts. let them decide
      flash({'msg':f'Invitation was for ' + invitation.invited_email + ' but you are logged in as ' + current_user.email, 'level':'warning'})
  elif User.select().where(User.email == invitation.invited_email):
    # assume cookies were cleared
    flash({'msg':f'Please log in as ' + invitation.invited_email, 'level':'warning'})
    return redirect(url_for('login'))
  else:
    enlist = EnlistNewUser()
    if not enlist.is_submitted():
      # auto populate the email from the invitation but allow the user to change it
      enlist.email.process_data(invitation.invited_email)

  if enlist.is_submitted():
    is_valid = enlist.validate()
    if enlist.csrf_token.errors:  # csrf must validate even for decline
      flash({'msg':f'Validation error', 'level':'danger'})
      return redirect(url_for('home'))
    if enlist.decline.data:  # don't validate form for decline, just decline
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
    elif is_valid:
      with db.atomic() as transaction:
        try:
          if isinstance(enlist, EnlistNewUser):
            u = User(name=enlist.data['name'],
                     email=enlist.data['email'])
            u.set_password(enlist.data['password'])
            u.save()
          else:
            u = User.get(User.id == current_user.id)

          tu = TeamUser(team=invitation.team, user=u)
          tu.save()

          invitation.status = 'accepted'
          invitation.save()
        except IntegrityError:
          transaction.rollback()
          flash({'msg':f'Email already registered. Please sign-in', 'level': 'danger'})
        except DatabaseError:
          transaction.rollback()
          flash({'msg':f'Database error', 'level':'danger'})
        else:
          if isinstance(enlist, EnlistNewUser) and not current_user.is_authenticated:
            login_user(u)
        return redirect(url_for('dashboard'))

  return render_template('enlist.html', enlist=enlist, invitation=invitation)

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

  return render_template('profile.html', can_edit=is_me, user=user)

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

  elif table_name == 'pledge':
    try:
      pledge = Pledge.get(Pledge.id == object_id)
    except Pledge.DoesNotExist:
      return jsonify({'ok': False})
    if current_user.id != pledge.user_id:
      return jsonify({'ok': False})

    with db.atomic() as transaction:
      try:
        if field_name == 'fulfilled':
          fulfilled = (value == 'true')
          pledge.fulfilled = fulfilled
          if fulfilled:
            pledge.fulfilled_at = pendulum.now()
          pledge.save()
      except DatabaseError:
        transaction.rollback()
        return jsonify({'ok': False})
      else:
        return jsonify({'ok': True})

  return jsonify({'ok': False})

@app.context_processor
def gravatar():
  def write_gravatar_link(email, size=100, default='mp'):
    url = 'https://www.gravatar.com/avatar/'
    hash_email = hashlib.md5(email.encode('ascii')).hexdigest()
    link = "{url}{hash_email}?s={size}&d={default}".format(url=url, hash_email=hash_email, size=size, default=default)
    return link
  return dict(gravatar=write_gravatar_link)

@app.before_request
def mock_time():
  try:
    fake_time = request.values.get('now')
    now = pendulum.parse(fake_time)
    pendulum.set_test_now(now)
  except:
    pass

@app.teardown_request
def unmock_time(response):
  pendulum.set_test_now()

@app.route('/health')
def health():
  db.connect(reuse_if_open=True)
  return jsonify({'OK': True})
