
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, SubmitField
from wtforms.validators import Email, Length

_PITCH="""I am organizing a crew of volunteers to take climate change action through a site called Spaceship Earth. Hoping you will join!"""

def list_of_emails(form, field):
  for email in field.data.split():
    Email()(email, field=field)

class Invite(FlaskForm):
  subject = TextField('Subject:', default='Invitation to join', render_kw={'disabled': True})
  emails = TextAreaField('To:', validators=[Length(min=1), list_of_emails],
      description='Enter one or more email addresses separated by spaces.',
      render_kw={'placeholder': 'bob@example.com mary@example.com', 'rows': 1})
  message = TextAreaField('Message:', default=_PITCH, render_kw={'rows': 5})
  invite = SubmitField('Send Invitations')
