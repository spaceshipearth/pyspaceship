
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, Length

class Login(FlaskForm):
  email = StringField(
      'Email', validators=[Email()], render_kw={'autofocus': True})
  password = PasswordField(
      'Password', validators=[Length(min=6)])
  login = SubmitField('Log In')
