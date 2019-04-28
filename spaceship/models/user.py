
from peewee import *
from playhouse.hybrid import hybrid_property
import pendulum
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import BaseModel

from .custom_fields import PendulumDateTimeField

class User(BaseModel):
  id = AutoField(primary_key=True)
  email = CharField(unique=True)
  name = CharField(default='')
  password_hash = CharField(null=True)
  created_at = PendulumDateTimeField(default=lambda: pendulum.now('UTC'))
  deleted_at = PendulumDateTimeField(null=True)
  email_confirmed = BooleanField(default=False)

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
