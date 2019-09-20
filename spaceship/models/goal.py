
import pendulum

from spaceship.db import db
from spaceship.models.custom_fields import PendulumDateTimeField
from sqlalchemy.ext.hybrid import hybrid_property
from enum import Enum

class Goal(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  short_description = db.Column(db.Text)
  category = db.Column(db.String(127), default='diet')

  created_at = db.Column(PendulumDateTimeField(), default=lambda: pendulum.now('UTC'))
  deleted_at = db.Column(PendulumDateTimeField(), nullable=True)

  @hybrid_property
  def is_deleted(self):
    return self.deleted_at == None

