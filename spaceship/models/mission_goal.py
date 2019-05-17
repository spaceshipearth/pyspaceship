
from peewee import *
from playhouse.hybrid import hybrid_property
import pendulum

from ..db import BaseModel

from .custom_fields import PendulumDateTimeField
from .mission import Mission
from .goal import Goal

class MissionGoal(BaseModel):
  mission = ForeignKeyField(Mission, backref='memberships')
  goal = ForeignKeyField(Goal, backref='memberships')
  week = SmallIntegerField()
  created_at = PendulumDateTimeField(default=lambda: pendulum.now('UTC'))
  deleted_at = PendulumDateTimeField(null=True)
