# ~*~ coding: utf-8 ~*~
"""
Some custom field types we use with PeeWee
"""

import datetime
import pendulum

from peewee import DateTimeField

class PendulumDateTimeField(DateTimeField):
  """Peewee field that produces Pendulum_ instances from Peewee fields.

  The big advantages to this are automatic timezone setting and that
  Pendulum is much nicer than the built in `datetime`

  Stolen from:
    https://github.com/croscon/fleaker/blob/046b026b79c9912bceebb17114bc0c5d2d02e3c7/fleaker/peewee/fields/pendulum.py

  Pendulum: https://pendulum.eustace.io/
  """
  def python_value(self, value):
    """Return the value in the database as an Pendulum object.

    Returns:
        pendulum.datetime:
            An instance of Pendulum with the field filled in.
    """
    value = super(PendulumDateTimeField, self).python_value(value)

    if isinstance(value, datetime.datetime):
      value = pendulum.instance(value)
    elif isinstance(value, datetime.date):
      value = pendulum.instance(
          datetime.datetime.combine(
            value, datetime.datetime.min.time()
            )
          )
    elif isinstance(value, str):
      value = pendulum.parse(value)

    return value

  def db_value(self, value):
    """Convert the Pendulum instance to a datetime for saving in the db."""
    if isinstance(value, pendulum.DateTime):
      value = datetime.datetime(
          value.year, value.month, value.day, value.hour, value.minute,
          value.second, value.microsecond, value.tzinfo
          )

    return super(PendulumDateTimeField, self).db_value(value)
