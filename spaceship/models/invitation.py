import pendulum
import uuid
from sqlalchemy.ext.hybrid import hybrid_property

from spaceship.db import db
from spaceship.models.custom_fields import PendulumDateTimeField

class Invitation(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  key_for_sharing = db.Column(
    db.String(40), nullable=False, unique=True, default=lambda: str(uuid.uuid4()))

  inviter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  inviter = db.relationship('User', lazy='joined', backref='invites')

  team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
  team = db.relationship('Team', lazy='joined', backref='invitations')

  invited_email = db.Column(db.String(127))
  message = db.Column(db.Text)
  status = db.Column(db.String(127))

  created_at = db.Column(PendulumDateTimeField(), default=lambda: pendulum.now('UTC'))
  deleted_at = db.Column(PendulumDateTimeField(), nullable=True)

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None

  @property
  def already_accepted(self):
    self.status == 'accepted'

  def mark_accepted(self):
    self.status = 'accepted'
