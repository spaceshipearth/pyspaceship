
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, EqualTo, Length

class Register(FlaskForm):
  name = StringField(
      'Name', validators=[Length(min=1)], render_kw={'autofocus': True})
  email = StringField(
      'Email', validators=[Email()])
  password = PasswordField(
      'Password', validators=[Length(min=6)])
  register = SubmitField('Register')
