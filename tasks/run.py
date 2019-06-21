
from invoke import task, run, Responder

from tasks.utils import ROOT_REPO_DIR, in_repo_root

PORT = 9876
FLASK_ENV = {
  'FLASK_APP':'spaceship',
}

def get_db_manager():
  from spaceship.db import db
  db.connect()
  return DatabaseManager(db)

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

  if debug:
    FLASK_ENV['FLASK_DEBUG'] = '1'

  # load sendgrid key if present
  try:
    file = open("sendgrid.key", "r")
    FLASK_ENV['SENDGRID_KEY'] = file.readline().strip()
  except:
    pass

  with ctx.cd(ROOT_REPO_DIR):
    ctx.run(f'flask run -h {host} -p {PORT}', env=FLASK_ENV)

@task
def shell(ctx):
  """Run the flask shell"""
  with ctx.cd(ROOT_REPO_DIR):
    ctx.run(f'flask shell', env=FLASK_ENV, pty=True)

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
def celery_worker(ctx):
  """run the celery worker"""
  with ctx.cd(ROOT_REPO_DIR):
    ctx.run(f'celery worker -A spaceship.celery.celery')

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
    run(f'flask db migrate -m "{desc}"', env=FLASK_ENV)

@task
def upgrade(ctx):
  """Runs pending migrations"""
  with ctx.cd(ROOT_REPO_DIR):
    run(f'flask db upgrade', env=FLASK_ENV)

@task
def downgrade(ctx):
  """Removes the last migration that ran"""
  with ctx.cd(ROOT_REPO_DIR):
    run(f'flask db downgrade', env=FLASK_ENV)
