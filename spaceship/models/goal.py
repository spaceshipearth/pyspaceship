
import pendulum

from spaceship.db import db
from spaceship.models.custom_fields import PendulumDateTimeField
from sqlalchemy.ext.hybrid import hybrid_property
from enum import Enum

GOALS = {}
class GoalTemplate(object):
  def __init__(self, category, short_name, short_description):
    self.category = category
    self.short_name = short_name
    self.short_description = short_description
    if not category in GOALS:
      GOALS[category] = []
    GOALS[category].append(self)

GoalTemplate('diet', 'beefless', 'Eat no beef for the duration of the mission.')
GoalTemplate('diet', 'vegeterian', 'Eat vegeterian food exclusively.')
GoalTemplate('diet', 'vegan', 'Eat vegan food exclusively.')

class Goal(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  short_description = db.Column(db.Text)
  category = db.Column(db.String(127), default='diet')

  created_at = db.Column(PendulumDateTimeField(), default=lambda: pendulum.now('UTC'))
  deleted_at = db.Column(PendulumDateTimeField(), nullable=True)

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None

