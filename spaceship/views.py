
from flask import render_template, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from peewee import DatabaseError, IntegrityError

from . import app

from .db import db
from .models.user import User
from .models.team import Team
from .models.team_user import TeamUser
from .models.invitation import Invitation
from .forms.register import Register
from .forms.login import Login
from .forms.invite import Invite

import uuid

@app.route('/')
def home():
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

@app.route('/dashboard')
@login_required
def dashboard():
  teams = (Team
            .select()
            .join(TeamUser)
            .join(User)
            .where(User.id == current_user.id))

  return render_template('dashboard.html', teams=teams)

@app.route('/register', methods=['GET', 'POST'])
def register():
  register = Register()

  if register.validate_on_submit():
    error_saving = False
    with db.atomic() as transaction:
      try:
        u = User(name=register.data['name'],
                 email=register.data['email'])
        u.set_password(register.data['password'])
        u.save()

        t = Team(captain=u, name="Serenity")
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
    return redirect(url_for('dashboard'))

  return render_template('register.html', register=register)

@app.route('/roster/<team_id>', methods=['GET', 'POST'])
@login_required
def roster(team_id):
  bad_team = f'Could not find team'
  try:
    team = Team.get(Team.id == team_id)
  except DoesNotExist:
    flash({'msg': bad_team, 'level': 'danger'})
    return redirect(url_for('dashboard'))
  if team.captain_id != current_user.id:
    flash({'msg': bad_team, 'level': 'danger'})
    return redirect(url_for('dashboard'))

  invite = Invite()
  if invite.validate_on_submit():
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
        raise
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

  return render_template('roster.html', team=team, roster=roster, invitations=invitations, invite=invite)

@app.route('/logout')
def logout():
  logout_user()
  flash({'msg':'Logged out successfully', 'level':'success'})
  return redirect(url_for('home'))

@app.route('/health')
def health():
  return jsonify({'OK': True})
