
from peewee import *
from playhouse.hybrid import hybrid_property
import pendulum

from ..db import BaseModel

from .custom_fields import PendulumDateTimeField
from .user import User
from .team import Team

class TeamUser(BaseModel):
  user = ForeignKeyField(User, backref='memberships')
  team = ForeignKeyField(Team, backref='memberships')
  created_at = PendulumDateTimeField(default=lambda: pendulum.now('UTC'))
  deleted_at = PendulumDateTimeField(null=True)

