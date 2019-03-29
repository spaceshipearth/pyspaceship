
from flask import render_template, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from peewee import DatabaseError, IntegrityError

from . import app

from .db import db
from .models.user import User
from .models.team import Team
from .models.team_user import TeamUser
from .forms.register import Register
from .forms.login import Login

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
        u = User(email=register.data['email'])
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

@app.route('/logout')
def logout():
  logout_user()
  flash({'msg':'Logged out successfully', 'level':'success'})
  return redirect(url_for('home'))

@app.route('/health')
def health():
  return jsonify({'OK': True})
