# ~*~ coding: utf-8 ~*~
"""
Some custom field types we use with PeeWee
"""

import pendulum

from sqlalchemy.types import TypeDecorator, DateTime

class PendulumDateTimeField(TypeDecorator):
  """Custom type to save/return pendulum datetime objects

  loosely based on:
    https://github.com/kvesteri/sqlalchemy-utils/blob/master/sqlalchemy_utils/types/arrow.py

  Pendulum: https://pendulum.eustace.io/
  """
  impl = DateTime

  def process_bind_param(self, value, dialect):
    if isinstance(value, pendulum.DateTime):
      return value.format('YYYY-MM-DD HH:mm:ss')

    return value

  def process_result_value(self, value, dialect):
    if value is not None:
      value = pendulum.instance(value)
    return value
