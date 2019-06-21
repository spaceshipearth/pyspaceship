
from celery import Celery

from . import app
host, port, db = app.config['REDIS_HOST'], app.config['REDIS_PORT'], app.config['REDIS_DB']

celery = Celery(app.name, broker=f"redis://{host}:{port}/{db}")
celery.conf.task_serializer = 'json'
celery.conf.always_eager = not app.config['USE_CELERY_WORKERS']
