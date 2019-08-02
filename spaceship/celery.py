
from celery import Celery

from spaceship import app
from spaceship.db import db as sqlalchemy_db

host, port, db = app.config['REDIS_HOST'], app.config['REDIS_PORT'], app.config['REDIS_DB']

celery = Celery(app.name, broker=f"redis://{host}:{port}/{db}")
celery.conf.task_serializer = 'json'
celery.conf.always_eager = not app.config['USE_CELERY_WORKERS']

class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection to the
    database is closed on task completion"""

    # this apparently keeps the task from being registered in some task
    # database if instantiated?
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """when the task is complete, auto-commit or auto-rollback the session"""
        if einfo:
            sqlalchemy_db.session.rollback()
        else:
            sqlalchemy_db.session.commit()

        sqlalchemy_db.session.remove()
