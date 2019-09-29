
import pendulum

from spaceship.db import db
from spaceship.models.custom_fields import PendulumDateTimeField
from sqlalchemy.ext.hybrid import hybrid_property

class Goal(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  short_description = db.Column(db.Text)
  category = db.Column(db.String(127), default='diet')

  created_at = db.Column(PendulumDateTimeField(), default=lambda: pendulum.now('UTC'))
  deleted_at = db.Column(PendulumDateTimeField(), nullable=True)

  visible_after = db.Column(PendulumDateTimeField(), nullable=True)
  hidden_after = db.Column(PendulumDateTimeField(), nullable=True)

  @hybrid_property
  def is_visible(self):
    now = pendulum.now('UTC')
    return (
      ((self.visible_after == None) | (self.visible_after < now)) &
      ((self.hidden_after == None) | (self.hidden_after > now))
    )

  @hybrid_property
  def is_deleted(self):
    return self.deleted_at == None
