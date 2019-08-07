
import logging
import pendulum
import tasktiger

from spaceship import logs
from spaceship.redis import store

class DBManager:
  """A context manager that helps deal with DB sessions in tasks"""
  def __init__(self):
    self.log = logging.getLogger('tiger.dbmanager')

    from spaceship.db import db
    self.db = db

  def __enter__(self):
    self.log.debug("disposing of db engine")
    self.db.engine.dispose()

  def __exit__(self, ex_type, ex_value, ex_tb):
    if ex_type:
      self.log.warning(f"task failed with {ex_type}; rolling back db")
      self.db.session.rollback()
    else:
      self.log.info("task complete; committing session")
      self.db.session.commit()

tiger = tasktiger.TaskTiger(
  connection=store,
  config={
    "CHILD_CONTEXT_MANAGERS": [DBManager()],
    "STORE_TRACEBACKS": False,
  },
)
