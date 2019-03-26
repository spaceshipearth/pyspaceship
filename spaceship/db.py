
# allows us to use a db URL
from playhouse.db_url import connect

# rest of peewee
from peewee import Model

# we get configuration from the app instance
from . import app

app.logger.info(f"Connecting to mysql at {app.config['MYSQL_HOST']}")
db = connect(app.config['MYSQL_URL'])
db.connect()

# base class for all models
class BaseModel(Model):
  class Meta:
    database = db
