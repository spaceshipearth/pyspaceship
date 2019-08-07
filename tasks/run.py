import os
from invoke import task, run, Responder

from tasks.utils import ROOT_REPO_DIR

PORT = 9876

def make_flask_env():
  env = {
    'FLASK_APP':'spaceship',
  }

  # load sendgrid key if present
  try:
    with open(os.path.join(ROOT_REPO_DIR, 'sendgrid.key')) as f:
      env['SENDGRID_KEY'] = f.readline().strip()
  except FileNotFoundError:
    pass

  return env

@task(
  default=True,
  help={
    'debug': 'Whether to run flask in DEBUG mode (Default: True)',
    'host': 'Host name to bind to (default: localhost)',
  },
)
def flask(ctx, host='localhost', debug=True):
  """Runs the flask web server"""
  print(f"Running Flask on localhost:{PORT}...")

  env = make_flask_env()
  if debug:
    env['FLASK_DEBUG'] = '1'

  with ctx.cd(ROOT_REPO_DIR):
    ctx.run(f'flask run -h {host} -p {PORT}', env=env)

@task
def shell(ctx):
  """Run the flask shell"""
  with ctx.cd(ROOT_REPO_DIR):
    ctx.run(f'flask shell', env=make_flask_env(), pty=True)

@task()
def gunicorn(ctx):
  """Runs the server via gunicorn"""
  print(f"Running gunicorn on localhost:{PORT}...")

  with ctx.cd(ROOT_REPO_DIR):
    ctx.run(f'gunicorn spaceship:app --bind 0.0.0.0:{PORT} --access-logfile -')

@task(
  help={
    'stop': 'Stop the running instance',
  },
)
def mysql(ctx, stop=False):
  """Runs mysql (and redis!) in docker-compose"""
  if stop:
    run('docker-compose stop')
  else:
    run('docker-compose up -d')

@task
def worker(ctx):
  """run the worker"""
  with ctx.cd(ROOT_REPO_DIR):
    ctx.run(f'celery worker -A spaceship.celery.celery', env=make_flask_env())

@task
def mysql_client(ctx):
  """Run a MySQL client connected to local dev DB"""
  from spaceship.config import Config

  responder = Responder(
    pattern="Enter password:",
    response=f"{Config.MYSQL_PASSWORD}\n",
  )

  mysql_cmd = " ".join([
    'mysql',
    '-h', Config.MYSQL_HOST,
    '-P', str(Config.MYSQL_PORT),
    '-u', Config.MYSQL_USERNAME,
    f'--database={Config.MYSQL_DB}',
    '-p'
  ])

  run(mysql_cmd, pty=True, watchers=[responder])

@task(
  help={
    'desc': 'Description of the migration',
  }
)
def prep_migration(ctx, desc):
  """Creates a migration based on changes to model files"""
  with ctx.cd(ROOT_REPO_DIR):
    run(f'flask db migrate -m "{desc}"', env=make_flask_env())

@task(
  help={
    'desc': 'Description of the migration',
  }
)
def prep_revision(ctx, desc):
  """Creates a migration based on changes to model files"""
  with ctx.cd(ROOT_REPO_DIR):
    run(f'flask db revision -m "{desc}"', env=make_flask_env())


@task
def upgrade(ctx):
  """Runs pending migrations"""
  with ctx.cd(ROOT_REPO_DIR):
    run(f'flask db upgrade', env=make_flask_env())

@task
def downgrade(ctx):
  """Removes the last migration that ran"""
  with ctx.cd(ROOT_REPO_DIR):
    run(f'flask db downgrade', env=make_flask_env())
