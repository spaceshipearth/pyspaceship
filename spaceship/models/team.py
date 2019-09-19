import pendulum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

from spaceship.db import db
from spaceship.models import TeamUser, Invitation
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

  def generic_invitation_from(self, inviter):
    try:
      generic = next(
        i for i in self.invitations if (
          i.inviter == inviter and i.invited_email is None and not i.already_accepted
        )
      )
    except StopIteration:
      generic = Invitation(
        inviter=inviter,
        team=self,
      )
      generic.save()

    return generic

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None
