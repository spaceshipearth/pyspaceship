
from invoke import task, run

import json
import random
import string

from . import utils

def get_pods():
  """List running pods"""
  items = json.loads(run('kubectl get pods -l app=pyspaceship -o=json', hide=True).stdout)['items']
  pods = []
  for item in items:
    pods.append({
      'name': item['metadata']['name'],
      'image': item['status']['containerStatuses'][0]['image'],
      'phase': item['status']['phase'],
    })

  return pods

@task
def pods(ctx):
  """Display existing pods for the service"""
  print('Phase\tImage\tName')
  print('------------------------------')
  for pod in get_pods():
    print(f'{pod["phase"]}\t{pod["image"]}\t{pod["name"]}')

@task(
  help={
    'host': 'MySQL host',
    'password': 'MySQL password',
    'username': "MySQL username (default: 'spaceship-app')",
    'db': "Name of the mysql database (default: 'spaceship')",
  }
)
def mysql_secret(ctx, host, password, username = 'spaceship-app', db = 'spaceship'):
  """Create a secret containing mysql credentials"""
  secret = utils.load_manifest('mysql_secret', {
    'host': host,
    'username': username,
    'password': password,
    'db': db,
  })

  utils.k8s_apply(secret, dry_run = False)

@task()
def session_secret(ctx, secret_key = None):
  def random_string(length):
    return "".join( random.SystemRandom().choices(string.ascii_letters + string.digits, k=length))

  if not secret_key:
    secret_key = random_string(24)

  secret = utils.load_manifest('session_secret', {
    'secret_key': secret_key,
  })

  utils.k8s_apply(secret, dry_run = False)

@task()
def run_migrations(ctx):
  """Migrate the DB that the cluster is connected to"""
  random_pod_name = [p['name'] for p in get_pods() if p['phase'] == 'Running'].pop()

  print(f"Using pod {random_pod_name} to run migrations...")
  run(f'kubectl exec {random_pod_name} inv run.upgrade')

@task
def bounce(ctx):
  """Bounce the deployment by deleting all pods and allowing them to be recreated"""
  for pod_name in [p['name'] for p in get_pods() if p['phase'] == 'Running']:
    run(f'kubectl delete pod {pod_name}')

@task
def logs(ctx):
  """Read the latest logs"""
  output = json.loads(
    run('gcloud logging read logName=projects/spaceshipearthprod/logs/pyspaceship --format json --freshness 1d --order desc', hide=True).stdout)
  for line in output:
    print(line['textPayload'])


@task()
def shell(ctx):
  """Get a shell on a random pod"""
  random_pod_name = [p['name'] for p in get_pods() if p['phase'] == 'Running'].pop()

  print(f"Picked pod {random_pod_name} for shell access...")
  run(f'kubectl exec -i -t {random_pod_name} -- /bin/bash', pty=True)
