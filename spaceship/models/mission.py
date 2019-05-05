
from peewee import *
from playhouse.hybrid import hybrid_property
import pendulum

from ..db import BaseModel

from .custom_fields import PendulumDateTimeField

class Mission(BaseModel):
  id = AutoField(primary_key=True)
  title = CharField()
  short_description = CharField()
  duration_in_weeks = SmallIntegerField(default=4)
  frozen = BooleanField(default=False)
  started_at = PendulumDateTimeField(null=True)
  created_at = PendulumDateTimeField(default=lambda: pendulum.now('UTC'))
  deleted_at = PendulumDateTimeField(null=True)

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None

  def start(self):
    return self.clone(start=True)

  def clone(self, start=False):
    clone = Mission()
    clone.title = self.title
    clone.short_description = self.short_description
    if start:
      clone.frozen = True
      clone.started_at = pendulum.now('UTC')
    clone.save()
    # import here instead of top-level to avoid a cycle
    from .mission_goal import MissionGoal
    for slot in self.goal_slots():
      clone_slot = MissionGoal(mission=clone, goal=slot.goal, week=slot.week)
      clone_slot.save()
    return clone

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
