
from flask_wtf import FlaskForm
from wtforms import SubmitField

class StartMission(FlaskForm):
  start = SubmitField('Start Mission')
