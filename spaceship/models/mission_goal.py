import pendulum

from ..db import db
from .custom_fields import PendulumDateTimeField
from sqlalchemy.ext.hybrid import hybrid_property

class MissionGoal(db.Model):
  mission_id = db.Column(db.Integer, db.ForeignKey('mission.id'), primary_key=True)
  mission = db.relationship('Mission', backref='mission_goals', single_parent=True, cascade='all, delete-orphan')

  goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), primary_key=True)
  goal = db.relationship('Goal', backref='goal_missions')

  week = db.Column(db.SmallInteger)

  created_at = db.Column(PendulumDateTimeField(), default=lambda: pendulum.now('UTC'))
  deleted_at = db.Column(PendulumDateTimeField(), nullable=True)

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None
