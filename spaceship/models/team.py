
from peewee import *
from playhouse.hybrid import hybrid_property
import pendulum

from ..db import BaseModel

from .custom_fields import PendulumDateTimeField
from .user import User
from .mission import Mission

class Team(BaseModel):
  id = AutoField(primary_key=True)
  captain = ForeignKeyField(User, backref='teams')
  name = CharField()
#  description = TextField(default='Best. Crew. Ever.')
  created_at = PendulumDateTimeField(default=lambda: pendulum.now('UTC'))
  deleted_at = PendulumDateTimeField(null=True)

  mission = ForeignKeyField(Mission, backref='mission', null=True)
  mission_start_at = PendulumDateTimeField(null=True)

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None

