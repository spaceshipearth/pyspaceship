
from invoke import task, run, Responder
from peewee_moves import DatabaseManager

from .utils import ROOT_REPO_DIR, in_repo_root

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
  },
)
def flask(ctx, debug=True):
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
    ctx.run(f'flask run -p {PORT}', env=FLASK_ENV)

@task
def shell(ctx):
  """Run the flask shell"""
  with ctx.cd(ROOT_REPO_DIR):
    ctx.run(f'flask shell', env=FLASK_ENV, pty=True)

@task(
  help={
    'force_prod': 'Set the IN_PRODUCTION variable to emulate production',
  }
)
def gunicorn(ctx, force_prod=False):
  """Runs the server via gunicorn"""
  print(f"Running gunicorn on localhost:{PORT}...")

  env = {'IN_PRODUCTION':'True'} if force_prod else {}
  with ctx.cd(ROOT_REPO_DIR):
    ctx.run(f'gunicorn spaceship:app --bind 0.0.0.0:{PORT} --access-logfile -', env=env)

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

@task
def migration_status(ctx):
  """Show the status of current migrations"""
  with in_repo_root():
    manager = get_db_manager()
    manager.status()

@task(
  help={
    'name': 'A name for the migration (like "adding col X to table Y")',
    'model': 'A model name (like "spaceship.models.user.User")',
  },
)
def migration_prep(ctx, name = None, model = None):
  """Create a migration file to alter DB schema"""
  with in_repo_root():
    manager = get_db_manager()

    if model:
      manager.create(model)
    elif name:
      manager.revision(name)
    else:
      raise ValueError("You must pass in either 'name' or 'model'")

@task(
  help={
    'target': 'The max version to apply (see run.migration-status)',
  }
)
def upgrade(ctx, target = None):
  """Apply pending migrations (or, optionally, only up to given target version)"""
  with in_repo_root():
    manager = get_db_manager()
    if target:
      manager.upgrade(target)
    else:
      manager.upgrade()

@task(
  help={
    'target': 'The version to migrate to (see run.migration-status)',
  }
)
def downgrade(ctx, target = None):
  """Undo last migration (or optionally, all since given target version)"""
  with in_repo_root():
    manager = get_db_manager()
    if target:
      manager.downgrade(target)
    else:
      manager.downgrade()
