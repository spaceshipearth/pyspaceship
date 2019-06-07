
import pendulum

from ..db import db
from .custom_fields import PendulumDateTimeField
from sqlalchemy.ext.hybrid import hybrid_property

class Achievement(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(127))

  short_description = db.Column(db.Text)
  badge_url = db.Column(db.String(256))

  created_at = db.Column(PendulumDateTimeField(), default=lambda: pendulum.now('UTC'))
  deleted_at = db.Column(PendulumDateTimeField(), nullable=True)

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None
