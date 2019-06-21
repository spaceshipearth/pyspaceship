import pendulum
from sqlalchemy.ext.hybrid import hybrid_property

from spaceship.db import db
from spaceship.models.custom_fields import PendulumDateTimeField

class MissionGoal(db.Model):
  mission_id = db.Column(db.Integer, db.ForeignKey('mission.id'), primary_key=True)
  mission = db.relationship('Mission', backref='mission_goals', single_parent=True, cascade='all, delete-orphan')

  goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), primary_key=True)
  goal = db.relationship('Goal', backref='goal_mission')

  week = db.Column(db.SmallInteger)

  created_at = db.Column(PendulumDateTimeField(), default=lambda: pendulum.now('UTC'))
  deleted_at = db.Column(PendulumDateTimeField(), nullable=True)

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None
