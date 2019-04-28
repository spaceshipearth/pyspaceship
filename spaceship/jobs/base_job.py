import logging

from rq import Queue

from .. import app
from ..redis import store

class BaseJob:
  """Convenience class to make delayed work with RQ easier

  Derive from this class and implement the classmethod `perform()`. You can
  execute jobs directly by calling `.perform()`, or call `.enqueue()` to send
  the work to a worker process.
  """

  # Default RQ settings for this job -- override in child classes
  QUEUE = 'default'    # what queue will the job go on?
  TIMEOUT_SECS = None  # how long to allow the job to run before failing it?
  TTL_SECS = -1        # how long to keep the job in the queue before giving up?
  RESULT_TTL_SECS = 500  # how long to keep the results in Redis?

  @classmethod
  def enqueue(cls, *args, **kwargs):
    q = Queue(
      cls.QUEUE,
      connection=store,

      # in dev, we won't use queues but invoke the job here-and-now
      is_async=app.config['IN_PRODUCTION'],
    )

    job = q.enqueue_call(
      func=cls.perform,
      args=args,
      kwargs=kwargs,
      timeout=cls.TIMEOUT_SECS,
      ttl=cls.TTL_SECS,
      result_ttl=cls.RESULT_TTL_SECS,
    )

    # we're not returning the job for now; hopefully we won't need it?
    return None

  @classmethod
  def log(cls):
    if not hasattr(cls, '_logger'):
      cls._logger = logging.getLogger(cls.__name__)
    return cls._logger

  @classmethod
  def perform(cls, *args, **kwargs):
    """This method should be overriden in child classes"""
    raise NotImplementedError()
