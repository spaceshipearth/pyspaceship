
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, EqualTo, Length

class Register(FlaskForm):
  email = StringField(
      'Email', validators=[Email()])
  confirm = StringField(
      'Confirm Email', validators=[EqualTo('email', message='Addresses must match')])
  password = PasswordField(
      'Password', validators=[Length(min=6)])
  register = SubmitField('Register')
