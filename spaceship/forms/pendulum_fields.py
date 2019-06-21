
import pendulum
from wtforms.fields import Field
from wtforms.widgets.html5 import DateTimeInput, DateInput


class DateTimeField(Field):
  """
  A text field which stores a `pendulum` instance matching a format.
  """

  widget = DateTimeInput()
  ERROR = 'Not a valid datetime value'

  def __init__(self, format="YYYY-MM-DD HH:mm:ss", **kwargs):
    super(DateTimeField, self).__init__(**kwargs)
    self.format = format

  def _value(self):
    if self.raw_data:
      return " ".join(self.raw_data)
    else:
      return self.data and self.data.format(self.format) or ""

  def process_formdata(self, valuelist):
    if valuelist:
      date_str = " ".join(valuelist)
      try:
        self.data = pendulum.from_format(date_str, self.format)
      except ValueError:
        self.data = None
        raise ValueError(self.gettext(self.ERROR))


class DateField(DateTimeField):
  """
  Same as DateTimeField, except stores a date
  """
  widget = DateInput()
  ERROR = 'Not a valid date value'

  def __init__(self, format="YYYY-MM-DD", **kwargs):
    super(DateField, self).__init__(**kwargs)
    self.format = format
