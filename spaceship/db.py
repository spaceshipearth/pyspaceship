
import logging
import pendulum
import pymysql.converters

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import DatabaseError

# set up flask-sqlalchemy
from spaceship import app

# log where we connect
logger = logging.getLogger('spaceship.db')
logger.info(f"Connecting to mysql at {app.config['MYSQL_HOST']}")

# connect to the DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# fix pendulum issues with datetime conversion
pymysql.converters.conversions[pendulum.DateTime] = pymysql.converters.escape_datetime

# commit my session on successful requests
# see: https://chase-seibert.github.io/blog/2016/03/31/flask-sqlalchemy-sessionless.html
@app.after_request
def session_commit(response):
  if response.status_code < 400:
    try:
      db.session.commit()
    except DatabaseError:
      db.session.rollback()
      raise

  return response

# import all models so they can be found by alembic (for migrations)
import spaceship.models
