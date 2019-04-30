import google.cloud.logging
import logging

from . import app

# enable google cloud logging
# from: https://cloud.google.com/logging/docs/setup/python
if app.config['USE_GOOGLE_LOGGING']:
  client = google.cloud.logging.Client()
  client.setup_logging()

  # set gunicorn logging to what google set up
  logger = logging.getLogger()
  google_handlers = logger.handlers

  gunicorn_logger = logging.getLogger('gunicorn.error')
  gunicorn_logger.handlers = google_handlers

# if google logging is not available, set up our own (to stdout)
else:
  # get our own logger that uses the same level as the app
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)

  # send output to stdout
  handler = logging.StreamHandler()
  logger.addHandler(handler)

  # our log format
  formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s : %(message)s')
  handler.setFormatter(formatter)

# output a message indicating we're booting up
logger = logging.getLogger('spaceship')
logger.warn(f"launching in an {app.config['COMPONENT']} environment...")
