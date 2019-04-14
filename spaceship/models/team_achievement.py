
from peewee import *
from playhouse.hybrid import hybrid_property
import pendulum

from ..db import BaseModel

from .custom_fields import PendulumDateTimeField
from .team import Team
from .achievement import Achievement

class TeamAchievement(BaseModel):
  id = AutoField(primary_key=True)
  team = ForeignKeyField(Team, backref='achievements')
  achievement = ForeignKeyField(Achievement, backref='teams')
  mission_completed = ForeignKeyField(Mission, backref='mission', null=True)
  created_at = PendulumDateTimeField(default=lambda: pendulum.now('UTC'))
  deleted_at = PendulumDateTimeField(null=True)

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None

