
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
    return self.clone(start=True, frozen=True)

  def clone(self, start=False, frozen=False):
    clone = Mission()
    clone.title = self.title
    clone.short_description = self.short_description
    clone.frozen = frozen
    if start:
      clone.started_at = pendulum.now('UTC')
    clone.save()
    from .mission_goal import MissionGoal
    for slot in self.goal_slots():
      clone_slot = MissionGoal(mission=clone, goal=slot.goal, week=slot.week)
      clone_slot.save()
    return clone

  def goal_slots(self, week=None):
    from .mission_goal import MissionGoal
    if week is None:
      return (MissionGoal
              .select()
              .where(MissionGoal.mission_id == self.id))
    return (MissionGoal
            .select()
            .where((MissionGoal.mission_id == self.id) &
                   (MissionGoal.week == week)))

  def serialize_for_js(self):
    schedule = []
    for week in range(1 + self.duration_in_weeks):
      schedule.append([{'goal_id': g.goal.id} for g in self.goal_slots(week=week)])
    return {'schedule': schedule}

  def update_from_js(self, state):
    from .mission_goal import MissionGoal
    schedule = state['schedule']
    self.duration_in_weeks = max(0, len(schedule) - 1)
    MissionGoal.delete().where(MissionGoal.mission_id == self.id).execute()
    for week_number, week in enumerate(schedule):
      for slot in week:
        MissionGoal.insert(mission_id=self.id,
                           goal_id=slot['goal_id'],
                           week=week_number).execute()
