import google.cloud.logging
import logging

from spaceship.config import Config

# enable google cloud logging
# from: https://cloud.google.com/logging/docs/setup/python
if Config.IN_PRODUCTION:
  client = google.cloud.logging.Client()
  client.setup_logging(log_level=logging.INFO)

# set log level on the root logger
root = logging.getLogger()
root.setLevel(logging.INFO)

# in production, set gunicorn handlers to what google provided
if Config.IN_PRODUCTION:
  gunicorn_logger = logging.getLogger('gunicorn.error')
  gunicorn_logger.handlers = root.handlers

# if google logging is not available, set up our own (to stdout)
else:
  # send output to stdout
  handler = logging.StreamHandler()
  root.addHandler(handler)

  # our log format
  formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s : %(message)s')
  handler.setFormatter(formatter)

# output a message indicating we're booting up
logging.getLogger('spaceship').warn('spaceship is launching...')
