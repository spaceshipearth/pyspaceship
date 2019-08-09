
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import Email, Length, NumberRange

class DietSurvey(FlaskForm):
    q1 = IntegerField(
        'How many meals per week (of ~21) do you usually have beef?',
        validators=[NumberRange(0, 21)], render_kw={'autofocus': True})
    q2 = IntegerField(
        'How many meals per week (of ~21) do you usually have other meat and fish?',
        validators=[NumberRange(0, 21)])
    q3 = IntegerField(
        'During the mission week, with how many meals did you eat beef?',
        validators=[NumberRange(0, 21)])
    q4 = IntegerField(
        'During the mission week, with how many meals did you eat other meat and fish?',
        validators=[NumberRange(0, 21)])
    q5 = StringField(
        'What surprised you about the mission?  What else do you want to share?',
        validators=[])
    submit = SubmitField('Submit')


