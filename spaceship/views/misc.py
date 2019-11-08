
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

def get_team_if_member(team_id):
  team = Team.query.get(team_id)
  if not team:
    return None

  if team not in current_user.teams:
    return None

  return team

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/contact')
def contact():
  return render_template('contact.html')

@app.route('/dashboard')
@login_required
def dashboard():
  missions = []
  for team in current_user.teams:
    missions.extend(team.missions)
  return render_template(
    'dashboard.html',
    categories=GOALS_BY_CATEGORY,
    teams=current_user.teams,
    completed_missions=[mission for mission in missions if mission.is_over],
    running_missions=[mission for mission in missions if mission.is_running],
    upcoming_missions=[mission for mission in missions if mission.is_upcoming],
    create_crew=CreateCrew())

def mission_goal_info(mission):
  goal=mission.goals[0]
  return [g for g in GOALS_BY_CATEGORY[goal.category]['goals'] if g['name'] == goal.short_description][0]

@app.route('/mission/<mission_uuid>')
def mission(mission_uuid):
  mission = Mission.query.filter(Mission.uuid == mission_uuid).one_or_none()
  invite_link= url_for('mission', mission_uuid=mission_uuid, _external=True)
  is_team_member = len([m for m in mission.team.members if m == current_user])
  return render_template('mission.html', mission=mission, goal=mission_goal_info(mission), team=mission.team,
      current_user=current_user, invite_link=invite_link, is_team_member=is_team_member)

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

MISSION_SURVEYS = {
  'diet': DietSurvey
}
@app.route('/mission/<mission_id>/debrief', methods=['GET', 'POST'])
def debrief(mission_id):
  mission = Mission.query.filter(Mission.id == mission_id).first()
  team_ids = map(lambda t: t.id, current_user.teams)
  if mission.team_id not in team_ids:
    raise ValueError('Unauthorized')

  survey = MISSION_SURVEYS[mission.goals[0].category]()
  if survey.validate_on_submit():
    objects = []
    for field in survey:
      if field.name in ['submit', 'csrf_token']:
        continue
      objects.append(
        SurveyAnswer(
            answer=survey.data[field.name],
            mission_id=mission_id,
            question_id=field.name,
            survey_version=1,
            user_id=current_user.id))
    db.session.bulk_save_objects(objects)
    return redirect(url_for('report', mission_id=mission_id))
  else:
    return render_template('eval.html', form=survey, mission=mission)

@app.route('/mission/<mission_id>/report', methods=['GET', 'POST'])
def report(mission_id):
  mission = Mission.query.filter(Mission.id == mission_id).first()
  team_ids = [t.id for t in current_user.teams]
  if mission.team_id not in team_ids:
    raise ValueError('Unauthorized')

  survey = MISSION_SURVEYS[mission.goals[0].category]()
  answers = list(SurveyAnswer.query.filter(SurveyAnswer.mission_id == mission_id))
  return render_template('report.html', form=survey, answers=answers, team_id=mission.team_id, mission=mission)

@app.route('/mission/create', methods=['POST'])
@login_required
def create_mission():
  category = request.form.get('category')
  goal_name = request.form.get('goal')
  if not category or not goal_name:
    flash({'msg': 'Error creating mission', 'level': 'danger'})
    return redirect(url_for('dashboard'))

  # make sure this is a valid goal name (we have info for it)
  goal_info = [g for g in GOALS_BY_CATEGORY[category]['goals'] if g['name'] == goal_name][0]

  # when should it start?
  now = pendulum.now('America/Los_Angeles')
  monday = now.next(pendulum.MONDAY)
  if (monday - now) < pendulum.duration(days=2):
    monday = monday.next(pendulum.MONDAY)

  # create a team for the mission
  team = create_team(current_user)
  team.save()

  goal = Goal(category=category, short_description=goal_name)
  goal.save()

  mission = Mission(
    duration_in_weeks=1,
    started_at=monday,
    team=team,
  )
  mission.goals.append(goal)
  mission.save()

  # schedule emails
  email.schedule_mission_emails(mission)

  # send to the mission page
  return redirect(url_for('mission', mission_uuid=mission.uuid))

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
