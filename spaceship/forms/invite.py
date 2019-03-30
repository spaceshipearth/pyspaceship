
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Email

def list_of_emails(form, field):
  for email in field.data.split():
    Email()(email, field=field)

class Invite(FlaskForm):
  message = TextAreaField('Message', default='Join my team!')
  emails = TextAreaField('Email(s)', validators=[list_of_emails],
      description='Enter one or more emails separated by spaces or new lines.',
      render_kw={'placeholder': 'bob@example.com mary@example.com'})
  invite = SubmitField('Send Invitations')
