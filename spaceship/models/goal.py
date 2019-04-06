
from peewee import *
from playhouse.hybrid import hybrid_property
import pendulum

from ..db import BaseModel

from .custom_fields import PendulumDateTimeField
from .mission import Mission

class Goal(BaseModel):
  id = AutoField(primary_key=True)
  mission = ForeignKeyField(Mission, backref='goals')
  week = SmallIntegerField()
  short_description = CharField()
  primary_for_mission = BooleanField()
  created_at = PendulumDateTimeField(default=lambda: pendulum.now('UTC'))
  deleted_at = PendulumDateTimeField(null=True)

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None