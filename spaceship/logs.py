import google.cloud.logging
import logging

from google.auth.exceptions import GoogleAuthError

# enable google cloud logging
# from: https://cloud.google.com/logging/docs/setup/python
try:
  client = google.cloud.logging.Client()
  client.setup_logging()

# if google logging is not available, set up our own (to stdout)
except GoogleAuthError:
  # get our own logger that uses the same level as the app
  logger = logging.getLogger('spaceship')
  logger.setLevel(logging.INFO)

  # send output to stdout
  handler = logging.StreamHandler()
  logger.addHandler(handler)

  # our log format
  formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s : %(message)s')
  handler.setFormatter(formatter)

# if google is configured, set gunicorn logging to what google set up
else:
  logger = logging.getLogger('spaceship')
  google_handlers = logger.handlers

  gunicorn_logger = logging.getLogger('gunicorn.error')
  gunicorn_logger.handlers = google_handlers

# output a message indicating we're booting up
logging.getLogger('spaceship').warn('spaceship is launching...')
