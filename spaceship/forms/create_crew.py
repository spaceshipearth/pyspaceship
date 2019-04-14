
from flask_wtf import FlaskForm
from wtforms import SubmitField

class CreateCrew(FlaskForm):
  create = SubmitField('Start a new crew')
