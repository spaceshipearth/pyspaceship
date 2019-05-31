
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

  @hybrid_property
  def start_time(self):
    return self.started_at.format('dddd [the] Do [of] MMMM')
  
  @hybrid_property
  def is_over(self):
    now = pendulum.now('UTC')
    mission_end_time = self.started_at.add(weeks=self.duration_in_weeks)
    return now >= mission_end_time

  @hybrid_property
  def is_running(self):
    now = pendulum.now('UTC')
    mission_end_time = self.started_at.add(weeks=self.duration_in_weeks)
    return now >= self.started_at and now <= mission_end_time

  @hybrid_property
  def is_upcoming(self):
    now = pendulum.now('UTC')
    return now < self.started_at