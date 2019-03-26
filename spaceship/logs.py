import logging

from . import app

# use gunicorn's loggers if those exist
gunicorn_logger = logging.getLogger('gunicorn.error')
gunicorn_handlers = gunicorn_logger.handlers

# we're running in gunicorn!
if gunicorn_handlers:
  app.logger.handlers = gunicorn_handlers
  app.logger.setLevel(gunicorn_logger.level)
