
from sqlalchemy.exc import DatabaseError

from flask_sqlalchemy.model import Model

from ..db import db

class MyBase(Model):
  @property
  def session(self):
    return db.session

  def save(self):
    self.session.add(self)
    self._flush()
    return self

  def update(self, **kwargs):
    for attr, value in kwargs.items():
      setattr(self, attr, value)
      return self.save()

  def delete(self):
    self.session.delete(self)
    self._flush()

  def refresh(self):
    self.session.refresh(self)

  def expire(self):
    self.session.expire(self)

  def _flush(self):
    try:
      self.session.flush()
    except DatabaseError:
      self.session.rollback()
      raise

db.Model = db.make_declarative_base(MyBase, db.metadata)
