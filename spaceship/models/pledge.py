
from peewee import *
from playhouse.hybrid import hybrid_property
import pendulum

from ..db import BaseModel

from .custom_fields import PendulumDateTimeField
from .user import User
from .goal import Goal

class Pledge(BaseModel):
  user = ForeignKeyField(User, backref='pledges')
  goal = ForeignKeyField(Goal, backref='pledges')
  fulfilled = BooleanField()
  start_at = PendulumDateTimeField(null=True)
  end_at = PendulumDateTimeField(null=True)
  created_at = PendulumDateTimeField(default=lambda: pendulum.now('UTC'))
  deleted_at = PendulumDateTimeField(null=True)
