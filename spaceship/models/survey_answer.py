
import pendulum

from spaceship.db import db
from spaceship.models.custom_fields import PendulumDateTimeField

from enum import Enum

class SurveyAnswer(db.Model):
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)

  mission_id = db.Column(db.Integer, db.ForeignKey('mission.id'), primary_key=True)
  mission = db.relationship('Mission', backref='mission_survey_answers', single_parent=True, cascade='all, delete-orphan')

  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
  user = db.relationship('User', backref='user_survey_answers', single_parent=True, cascade='all, delete-orphan')

  question_id = db.Column(db.String(5))
  answer = db.Column(db.String(256))

  survey_version = db.Column(db.Integer)

  created_at = db.Column(PendulumDateTimeField(), default=lambda: pendulum.now('UTC'))
  deleted_at = db.Column(PendulumDateTimeField(), nullable=True)

