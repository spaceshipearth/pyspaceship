
import pendulum
from sqlalchemy.ext.hybrid import hybrid_property

from spaceship.db import db
from spaceship.models.custom_fields import PendulumDateTimeField

class TeamUser(db.Model):
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
  user = db.relationship('User', backref='team_users')

  team_id = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)
  team = db.relationship('Team', backref='team_users')

  created_at = db.Column(PendulumDateTimeField(), default=lambda: pendulum.now('UTC'))
  deleted_at = db.Column(PendulumDateTimeField(), nullable=True)

  @hybrid_property
  def is_deleted(self):
    return self.deleted_at == None

