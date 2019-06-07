import pendulum

from ..db import db
from .custom_fields import PendulumDateTimeField

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

class Mission(db.Model):
  id = db.Column(db.Integer, primary_key=True)

  title = db.Column(db.String(127))
  short_description = db.Column(db.String(127))
  duration_in_weeks = db.Column(db.SmallInteger, default=4)
  frozen = db.Column(db.Boolean, default=False)

  started_at = db.Column(PendulumDateTimeField(), nullable=True)

  team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  team = db.relationship('Team', backref='missions')

  goals = association_proxy('mission_goal', 'goal')

  created_at = db.Column(PendulumDateTimeField(), default=lambda: pendulum.now('UTC'))
  deleted_at = db.Column(PendulumDateTimeField(), nullable=True)

  @property
  def is_active(self):
    return self.deleted_at == None

  @property
  def start_time_str(self):
    return self.started_at.format('dddd [the] Do [of] MMMM')

  @property
  def end_time_str(self):
    mission_end_time = self.started_at.add(weeks=self.duration_in_weeks)
    return mission_end_time.format('dddd [the] Do [of] MMMM')
  
  @property
  def is_over(self):
    now = pendulum.now('UTC')
    mission_end_time = self.started_at.add(weeks=self.duration_in_weeks)
    return now >= mission_end_time

  @property
  def is_running(self):
    now = pendulum.now('UTC')
    mission_end_time = self.started_at.add(weeks=self.duration_in_weeks)
    return now < mission_end_time and now >= self.started_at

  @property
  def is_upcoming(self):
    now = pendulum.now('UTC')
    return now < self.started_at

  @property
  def mission_day(self):
    return (pendulum.now('UTC') - self.started_at).in_days() 
