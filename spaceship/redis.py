import redis

from . import app

store = redis.Redis(
  host=app.config['REDIS_HOST'],
  port=app.config['REDIS_PORT'],
  db=app.config['REDIS_DB'],
)
