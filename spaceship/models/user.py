
import pendulum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.security import generate_password_hash, check_password_hash

from spaceship.db import db
from spaceship.models.custom_fields import PendulumDateTimeField

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(127), unique=True)
  name = db.Column(db.String(127), default='')
  password_hash = db.Column(db.String(127), nullable=True)

  email_confirmed = db.Column(db.Boolean, default=False)

  teams = association_proxy('team_users', 'team')

  created_at = db.Column(PendulumDateTimeField(), default=lambda: pendulum.now('UTC'))
  deleted_at = db.Column(PendulumDateTimeField(), nullable=True)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None

  # required by Flask Login
  @property
  def is_authenticated(self):
    return True
  @property
  def is_anonymous(self):
    return False
  def get_id(self):
    return str(self.id)
