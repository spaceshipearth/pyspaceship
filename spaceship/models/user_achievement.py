
from peewee import *
from playhouse.hybrid import hybrid_property
import pendulum

from ..db import BaseModel

from .custom_fields import PendulumDateTimeField
from .user import User
from .achievement import Achievement

class UserAchievement(BaseModel):
  id = AutoField(primary_key=True)
  user = ForeignKeyField(User, backref='achievements')
  name = CharField()
  created_at = PendulumDateTimeField(default=lambda: pendulum.now('UTC'))
  deleted_at = PendulumDateTimeField(null=True)

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None

