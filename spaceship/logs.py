import google.cloud.logging
import logging

from spaceship.config import Config

# enable google cloud logging
# from: https://cloud.google.com/logging/docs/setup/python
if Config.IN_PRODUCTION:
  client = google.cloud.logging.Client()
  client.setup_logging()

  # set gunicorn logging to what google set up
  root = logging.getLogger()
  google_handlers = root.handlers

  gunicorn_logger = logging.getLogger('gunicorn.error')
  gunicorn_logger.handlers = google_handlers

# if google logging is not available, set up our own (to stdout)
else:
  root = logging.getLogger()
  root.setLevel(logging.INFO)

  # send output to stdout
  handler = logging.StreamHandler()
  root.addHandler(handler)

  # our log format
  formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s : %(message)s')
  handler.setFormatter(formatter)

# output a message indicating we're booting up
logging.getLogger('spaceship').warn('spaceship is launching...')
