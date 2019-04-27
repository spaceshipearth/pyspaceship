
import logging

# rest of peewee
from peewee import Model
from playhouse.pool import PooledMySQLDatabase

# we get configuration from the app instance
from . import app

logger = logging.getLogger('spaceship.db')
logger.info(f"Connecting to mysql at {app.config['MYSQL_HOST']}")

db = PooledMySQLDatabase(
  app.config['MYSQL_DB'],
  host=app.config['MYSQL_HOST'],
  port=app.config['MYSQL_PORT'],
  user=app.config['MYSQL_USERNAME'],
  password=app.config['MYSQL_PASSWORD'],
  charset = 'utf8',
)

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
