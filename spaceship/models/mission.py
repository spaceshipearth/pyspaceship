
from peewee import *
from playhouse.hybrid import hybrid_property
import pendulum

from ..db import BaseModel
from .team import Team

from .custom_fields import PendulumDateTimeField

class Mission(BaseModel):
  id = AutoField(primary_key=True)
  title = CharField()
  short_description = CharField()
  duration_in_weeks = SmallIntegerField(default=4)
  frozen = BooleanField(default=False)
  started_at = PendulumDateTimeField(null=True)
  team_id = ForeignKeyField(Team, backref='missions')
  created_at = PendulumDateTimeField(default=lambda: pendulum.now('UTC'))
  deleted_at = PendulumDateTimeField(null=True)

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None
