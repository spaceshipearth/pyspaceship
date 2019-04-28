from invoke import task, run

from .utils import in_repo_root

def mkenv():
  with in_repo_root():
    from spaceship import app
    redis_url = ''.join([
      'redis://',
      app.config['REDIS_HOST'],
      ':',
      str(app.config['REDIS_PORT']),
      '/',
      str(app.config['REDIS_DB']),
    ])

    return {'RQ_REDIS_URL': redis_url}


@task(
  default=True,
)
def info(ctx):
  run('rq info', env=mkenv())

@task
def worker(ctx):
  run('rq worker', env=mkenv())
