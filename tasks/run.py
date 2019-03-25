
from invoke import task, run

PORT = 9876
FLASK_ENV = {
  'FLASK_APP':'spaceship',
}

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
  run(f'flask shell', env=FLASK_ENV)

@task()
def gunicorn(ctx):
  """Runs the server via gunicorn"""
  print(f"Running gunicorn on localhost:{PORT}...")
  run(f'gunicorn spaceship:app --bind 127.0.0.1:{PORT}')
