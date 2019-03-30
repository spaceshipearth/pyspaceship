
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, EqualTo, Length

from .register import Register

class EnlistNewUser(Register):
  decline = SubmitField('Decline')

class EnlistExistingUser(FlaskForm):
  accept = SubmitField('Accept')
  decline = SubmitField('Decline')
