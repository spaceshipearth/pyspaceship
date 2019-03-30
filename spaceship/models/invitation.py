
from peewee import *
from playhouse.hybrid import hybrid_property
import pendulum

from ..db import BaseModel

from .custom_fields import PendulumDateTimeField
from .user import User
from .team import Team

class Invitation(BaseModel):
  id = AutoField(primary_key=True)
  key_for_sharing = UUIDField()
  inviter = ForeignKeyField(User)
  team = ForeignKeyField(Team, backref='invitations')
  invited_email = CharField()
  message = TextField()
  status = CharField()
  created_at = PendulumDateTimeField(default=lambda: pendulum.now('UTC'))
  deleted_at = PendulumDateTimeField(null=True)

  def create_uri_path(self):
    self.uri_path = inviter.id + team.

  @hybrid_property
  def is_active(self):
    return self.deleted_at == None
