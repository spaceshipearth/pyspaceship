
from peewee import *
import pendulum
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import BaseModel

from .custom_fields import PendulumDateTimeField

class User(BaseModel):
  id = AutoField(primary_key=True)
  email = CharField(unique=True)
  password_hash = CharField()
  created_at = PendulumDateTimeField(default=lambda: pendulum.now('UTC'))
  deleted_at = PendulumDateTimeField(null=True)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)
