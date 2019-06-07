import datetime
from flask_wtf import FlaskForm
import wtforms
from wtforms.fields.html5 import DateField

def next_monday():
  weekday = 0 # monday
  today = datetime.date.today()
  days_ahead = weekday - today.weekday()
  if days_ahead <= 1: # we want at least 1 days notice 
      days_ahead += 7
  return today + datetime.timedelta(days_ahead)

class CreateMissionForm(FlaskForm):
  def __init__(self, team_id):
    super(CreateMissionForm, self).__init__()
    self.team_id.data = team_id
  
  goal = wtforms.SelectField(label='Mission goal', 
                          choices=[('beefless', 'Eat no beef'), 
                                  ('vegeterian', 'Eat a vegeterian diet'),
                                  ('vegan', 'Eat a vegan diet')])
  start = DateField(label='Mission start date', default=next_monday)
  duration = wtforms.SelectField(label='Mission duration', choices=[('1', 'One week')])
  create = wtforms.SubmitField('Create Mission')
  team_id = wtforms.HiddenField()
