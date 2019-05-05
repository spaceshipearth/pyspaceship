
from peewee import *
from playhouse.hybrid import hybrid_property
import pendulum

from ..db import BaseModel

from .custom_fields import PendulumDateTimeField

class Mission(BaseModel):
  id = AutoField(primary_key=True)
  title = CharField()
  short_description = CharField()
  created_at = PendulumDateTimeField(default=lambda: pendulum.now('UTC'))
  deleted_at = PendulumDateTimeField(null=True)

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None

  def goal_slots(self, week=None):
    # import here instead of top-level to avoid a cycle
    from .mission_goal import MissionGoal
    if week is None:
      return (MissionGoal
              .select()
              .where(MissionGoal.mission_id == self.id))
    return (MissionGoal
            .select()
            .where((MissionGoal.mission_id == self.id) &
                   (MissionGoal.week == week)))
