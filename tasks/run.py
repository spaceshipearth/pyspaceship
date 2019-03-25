
from invoke import task, run, Responder
from peewee_moves import DatabaseManager

PORT = 9876
FLASK_ENV = {
  'FLASK_APP':'spaceship',
}

def get_db_manager():
  from spaceship.db import db
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

  run(f'flask run -p {PORT}', env=FLASK_ENV)

@task
def shell(ctx):
  """Run the flask shell"""
  run(f'flask shell', env=FLASK_ENV, pty=True)

@task()
def gunicorn(ctx):
  """Runs the server via gunicorn"""
  print(f"Running gunicorn on localhost:{PORT}...")
  run(f'gunicorn spaceship:app --bind 127.0.0.1:{PORT}')

@task(
  help={
    'stop': 'Stop the running instance',
  },
)
def mysql(ctx, stop=False):
  """Runs mysql in docker-compose"""
  if stop:
    run('docker-compose stop')
  else:
    run('docker-compose up -d')

@task
def mysql_client(ctx):
  """Run a MySQL client connected to local dev DB"""
  responder = Responder(
    pattern="Enter password:",
    response="aa7925b6f7b\n",
  )

  run(
    'mysql -h 127.0.0.1 -P 9877 -u spaceship-app --database=spaceship -p',
    pty=True,
    watchers=[responder])

@task
def migration_status(ctx):
  """Show the status of current migrations"""
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
  manager = get_db_manager()
  if target:
    manager.downgrade(target)
  else:
    manager.downgrade()
