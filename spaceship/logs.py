import logging

from . import app

# use gunicorn's loggers if those exist
gunicorn_logger = logging.getLogger('gunicorn.error')
gunicorn_handlers = gunicorn_logger.handlers

# we're running in gunicorn!
if gunicorn_handlers:
  app.logger.handlers = gunicorn_handlers
  app.logger.setLevel(gunicorn_logger.level)

# get our own logger that uses the same level as the app
logger = logging.getLogger('spaceship')
logger.setLevel(app.logger.level)

# send output to stdout
handler = logging.StreamHandler()
logger.addHandler(handler)

# our log format
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s : %(message)s')
handler.setFormatter(formatter)
