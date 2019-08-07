import redis

from spaceship.config import Config

store = redis.Redis(
  host=Config.REDIS_HOST,
  port=Config.REDIS_PORT,
  db=Config.REDIS_DB,
  decode_responses=True,
)
