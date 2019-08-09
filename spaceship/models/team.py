import pendulum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

from spaceship.db import db
from spaceship.models import TeamUser
from spaceship.models.custom_fields import PendulumDateTimeField

class Team(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(127))
  description = db.Column(db.Text, default='Best. Crew. Ever.')

  captain_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  captain = db.relationship('User', backref='captain_of')

  members = association_proxy(
    'team_users', 'user', creator=lambda member: TeamUser(user=member))

  created_at = db.Column(PendulumDateTimeField(), default=lambda: pendulum.now('UTC'))
  deleted_at = db.Column(PendulumDateTimeField(), nullable=True)

  @hybrid_property
  def is_deleted(self):
    return self.deleted_at == None
