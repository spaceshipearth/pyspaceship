
import logging

# allows us to use a db URL
from playhouse.db_url import connect

# rest of peewee
from peewee import Model

# we get configuration from the app instance
from . import app

logger = logging.getLogger('spaceship.db')
logger.info(f"Connecting to mysql at {app.config['MYSQL_HOST']}")

db = connect(app.config['MYSQL_URL'])

@app.before_request
def open_db_connection():
  db.connect()

@app.teardown_request
def close_db_connection(exc):
  if not db.is_closed():
    db.close()

# base class for all models
class BaseModel(Model):
  class Meta:
    database = db
