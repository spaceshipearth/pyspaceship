from flask_wtf import FlaskForm
from wtforms import SubmitField

class AcceptInvitation(FlaskForm):
  accept = SubmitField('Accept')

class DeclineInvitation(FlaskForm):
  decline = SubmitField('Decline')
