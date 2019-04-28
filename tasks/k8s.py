
from invoke import task, run

import random
import string

from . import utils

@task
def pods(ctx):
  """Display existing pods for the service"""
  print('Phase\tImage\tName')
  print('------------------------------')
  for pod in utils.get_pods():
    print(f'{pod["phase"]}\t{pod["image"]}\t{pod["name"]}')

@task(
  help={
    'host': 'MySQL host',
    'password': 'MySQL password',
    'port': 'MySQL port (default: 3306)',
    'username': "MySQL username (default: 'spaceship-app')",
    'db': "Name of the mysql database (default: 'spaceship')",
  }
)
def mysql_secret(ctx, host, password, port=3306, username = 'spaceship-app', db = 'spaceship'):
  """Create a secret containing mysql credentials"""
  secret = utils.load_manifest('mysql_secret', {
    'host': host,
    'port': str(port),
    'username': username,
    'password': password,
    'db': db,
  })

  utils.k8s_apply(secret, dry_run = False)

@task(
  help={
    'host': 'Redis host',
    'port': 'Redis port (default: 6379)',
    'db': "Number of the Redis DB (default: '0')",
  }
)
def redis_secret(ctx, host, port=3306, db=0):
  """Create a secret containing redis credentials"""
  secret = utils.load_manifest('redis_secret', {
    'host': host,
    'port': str(port),
    'db': str(db),
  })

  utils.k8s_apply(secret, dry_run = False)

@task()
def session_secret(ctx, secret_key = None):
  """Creates a secret containing a session key

  Running this will invalidate all exising sessions and log out all users"""
  def random_string(length):
    return "".join( random.SystemRandom().choices(string.ascii_letters + string.digits, k=length))

  if not secret_key:
    secret_key = random_string(24)

  secret = utils.load_manifest('session_secret', {
    'secret_key': secret_key,
  })

  utils.k8s_apply(secret, dry_run = False)

@task()
def sendgrid_secret(ctx, secret_key = None):
  """creates secret containing key to authenticate with sendgrid"""
  secret = utils.load_manifest('sendgrid_secret', {
    'secret_key': secret_key,
  })

  utils.k8s_apply(secret, dry_run = False)

@task()
def google_app_secret(ctx, keyfile):
  """upload a keyfile as a google secret

  created by:
    gcloud iam service-accounts keys create /tmp/key.json --iam-account=pyspaceship@spaceshipearthprod.iam.gserviceaccount.com
  """
  secret = utils.load_manifest('google-app-creds', {
    'keyfile': open(keyfile).read().strip(),
  })

  utils.k8s_apply(secret, dry_run = False)

@task()
def run_migrations(ctx):
  """Migrate the DB that the cluster is connected to"""
  random_pod_name = utils.random_pod_name()

  print(f"Using pod {random_pod_name} to run migrations...")
  run(f'kubectl exec {random_pod_name} inv run.upgrade')

@task
def bounce(ctx):
  """Bounce the deployment by deleting all pods and allowing them to be recreated"""
  pod_names = [p['name'] for p in utils.get_pods() if p['phase'] == 'Running']
  for pod_name in pod_names:
    run(f'kubectl delete pod {pod_name}')

@task()
def shell(ctx):
  """Get a shell on a random pod"""
  random_pod_name = utils.random_pod_name()

  print(f"Picked pod {random_pod_name} for shell access...")
  run(f'kubectl exec -i -t {random_pod_name} -- /bin/bash', pty=True)
