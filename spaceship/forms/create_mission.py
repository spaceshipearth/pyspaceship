
from flask_wtf import FlaskForm
import pendulum
import wtforms
from spaceship.forms.pendulum_fields import DateField
from spaceship.models.goal import GOALS

def next_monday():
  now = pendulum.now('UTC')
  monday = now.next(pendulum.MONDAY)

  # we want at least 1 day's notice
  if (monday - now) < pendulum.duration(days=1):
    monday = monday.next(pendulum.MONDAY)

  return monday

class CreateMissionForm(FlaskForm):
  def __init__(self, team_id):
    super(CreateMissionForm, self).__init__()
    self.team_id.data = team_id
  
  goal = wtforms.SelectField(label='Mission goal', 
                           choices=[(goal.short_description, goal.short_description) for goal in GOALS['diet']])
  start = DateField(label='Mission start date', default=next_monday)
  duration = wtforms.SelectField(label='Mission duration', choices=[('1', 'One week')])
  create = wtforms.SubmitField('Create Mission')
  team_id = wtforms.HiddenField()
