import pendulum
from sqlalchemy.ext.hybrid import hybrid_property

from spaceship.db import db
from spaceship.models.custom_fields import PendulumDateTimeField

class Pledge(db.Model):
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

  mission_id = db.Column(db.Integer, db.ForeignKey('mission.id'), primary_key=True)
  mission = db.relationship('Mission', backref='pledges')

  goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), primary_key=True)
  goal = db.relationship('Goal', backref='pledges')

  fulfilled = db.Column(db.Boolean, default=False)
  start_at = db.Column(PendulumDateTimeField, nullable=True, default=None)
  end_at = db.Column(PendulumDateTimeField, nullable=True, default=None)

  created_at = db.Column(PendulumDateTimeField(), default=lambda: pendulum.now('UTC'))
  deleted_at = db.Column(PendulumDateTimeField(), nullable=True)

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None
