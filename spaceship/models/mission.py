import pendulum
import serpy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
import uuid

from spaceship.db import db
from spaceship.models import MissionGoal
from spaceship.models.custom_fields import PendulumDateTimeField

class Mission(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  uuid = db.Column(db.String(32), unique=True, default=lambda: uuid.uuid4().hex)

  title = db.Column(db.String(127), default='')
  short_description = db.Column(db.String(127), default='')
  duration_in_weeks = db.Column(db.SmallInteger, default=4)
  frozen = db.Column(db.Boolean, default=False)

  started_at = db.Column(PendulumDateTimeField(), nullable=True)

  team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  team = db.relationship('Team', backref='missions')

  goals = association_proxy(
    'mission_goals', 'goal', creator=lambda goal: MissionGoal(goal=goal))

  created_at = db.Column(PendulumDateTimeField(), default=lambda: pendulum.now('UTC'))
  deleted_at = db.Column(PendulumDateTimeField(), nullable=True)

  class Serializer(db.Model.Serializer):
    uuid = serpy.StrField()
    title = serpy.StrField()
    short_description = serpy.StrField()
    duration_in_weeks = serpy.IntField()

    goals = MissionGoal.Serializer(many=True)

  @property
  def is_deleted(self):
    return self.deleted_at != None

  @property
  def days_until_start(self):
    time_left = self.start_time - pendulum.now('UTC')
    return time_left.in_days()

  @property
  def primary_goal_str(self):
    if not self.goals:
      return None
    else:
      return self.goals[0].short_description

  @property
  def co2_saved_str(self):
    # todo: pull from DB
    return '345kg'

  @property
  def start_time_str(self):
    return self.started_at.format('dddd [the] Do [of] MMMM')

  @property
  def end_time(self):
    return self.started_at.add(weeks=self.duration_in_weeks)

  @property
  def end_time_str(self):
    return self.end_time.format('dddd [the] Do [of] MMMM')

  @property
  def is_over(self):
    now = pendulum.now('UTC')
    mission_end_time = self.started_at.add(weeks=self.duration_in_weeks)
    return now >= mission_end_time

  @property
  def is_running(self):
    now = pendulum.now('UTC')
    mission_end_time = self.started_at.add(weeks=self.duration_in_weeks)
    return now < mission_end_time and now >= self.started_at and not self.is_deleted

  @property
  def is_upcoming(self):
    now = pendulum.now('UTC')
    return now < self.started_at and not self.is_deleted

  @property
  def start_time(self):
    return self.started_at

  @property
  def end_time(self):
    return self.started_at.add(weeks=self.duration_in_weeks)

  @property
  def mission_day(self):
    return (pendulum.now('UTC') - self.started_at).in_days()

  @property
  def duration_in_days(self):
    return self.duration_in_weeks * 7
