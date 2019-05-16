
from invoke import task, run

import random
import string

from .utils import load_manifest, K8SNamespace, TEST_NAMESPACE

@task(
  help={
    'namespace': f"Version of the site (default: {TEST_NAMESPACE})",
  }
)
def pods(ctx, namespace=TEST_NAMESPACE):
  """Display existing pods for the service"""
  print('Phase\tImage\tName')
  print('------------------------------')
  with K8SNamespace(namespace) as ns:
    for pod in ns.get_pods():
      print(f'{pod["phase"]}\t{pod["image"]}\t{pod["name"]}')

@task
def ingress(ctx):
  """configure the ingress resource for all namespaces"""
  raise NotImplementedError('this does not work right now')
  ingress = load_manifest('ingress')
  ns.apply(ingress)

  info = json.loads(run('kubectl get ingress pyspaceship-ingress -o=json', hide=True).stdout)
  ingress = info['status']['loadBalancer']['ingress']
  print("Load balancer IPs:")
  for i in ingress:
    ip = i['ip']
    print(f'- {ip}')

@task(
  help={
    'host': 'MySQL host',
    'password': 'MySQL password',
    'port': 'MySQL port (default: 3306)',
    'username': "MySQL username (default: 'spaceship-app')",
    'db': "Name of the mysql database (default: 'spaceship')",
    'namespace': f"Version of the site (default: {TEST_NAMESPACE})",
  }
)
def mysql_secret(
    ctx,
    host,
    password,
    port=3306,
    username='spaceship-app',
    db='spaceship',
    namespace=TEST_NAMESPACE):
  """Create a secret containing mysql credentials"""
  secret = load_manifest('mysql_secret', {
    'host': host,
    'port': str(port),
    'username': username,
    'password': password,
    'db': db,
  })

  with K8SNamespace(namespace) as ns:
    ns.apply(secret)

@task(
  help={
    'namespace': f"Version of the site (default: {TEST_NAMESPACE})",
  }
)
def session_secret(ctx, secret_key = None, namespace = TEST_NAMESPACE):
  """Creates a new session secret; this will invalidate existing sessions"""
  def random_string(length):
    return "".join( random.SystemRandom().choices(string.ascii_letters + string.digits, k=length))

  if not secret_key:
    secret_key = random_string(24)

  secret = load_manifest('session_secret', {
    'secret_key': secret_key,
  })

  with K8SNamespace(namespace) as ns:
    ns.apply(secret)

@task(
  help={
    'secret-key': 'The token from sendgrid',
    'namespace': f"Version of the site (default: {TEST_NAMESPACE})",
  }
)
def sendgrid_secret(ctx, secret_key, namespace = TEST_NAMESPACE):
  """The secret to sending email"""
  secret = load_manifest('sendgrid_secret', {
    'secret_key': secret_key,
  })

  with K8SNamespace(namespace) as ns:
    ns.apply(secret)

@task(
  help={
    'keyfile': 'path to the json keyfile',
    'namespace': f"Version of the site (default: {TEST_NAMESPACE})",
  }
)
def google_app_secret(ctx, keyfile, namespace = TEST_NAMESPACE):
  """upload a keyfile as a google secret

  created by:
    gcloud iam service-accounts keys create /tmp/key.json --iam-account=pyspaceship@spaceshipearthprod.iam.gserviceaccount.com
  """
  secret = load_manifest('google-app-creds', {
    'keyfile': open(keyfile).read().strip(),
  })

  with K8SNamespace(namespace) as ns:
    ns.apply(secret)

@task(
  help={
    'namespace': f"Version of the site (default: {TEST_NAMESPACE})",
  }
)
def run_migrations(ctx, namespace = TEST_NAMESPACE):
  """Migrate the DB that the cluster is connected to"""
  with K8SNamespace(namespace) as ns:
    random_pod_name = ns.random_pod_name()

    print(f"Using pod {random_pod_name} to run migrations...")
    run(f'{ns.kubecmd} exec {random_pod_name} inv run.upgrade')

@task(
  help={
    'namespace': f"Version of the site (default: {TEST_NAMESPACE})",
  }
)
def bounce(ctx, namespace = TEST_NAMESPACE):
  """Bounce the deployment by deleting all pods and allowing them to be recreated"""
  with K8SNamespace(namespace) as ns:
    pod_names = [p['name'] for p in ns.get_pods() if p['phase'] == 'Running']
    for pod_name in pod_names:
      run(f'{ns.kubecmd} delete pod {pod_name}')

@task(
  help={
    'namespace': f"Version of the site (default: {TEST_NAMESPACE})",
  }
)
def shell(ctx, namespace = TEST_NAMESPACE):
  """Get a shell on a random pod"""
  with K8SNamespace(namespace) as ns:
    random_pod_name = ns.random_pod_name()

    print(f"Picked pod {random_pod_name} for shell access...")
    run(f'{ns.kubecmd} exec -i -t {random_pod_name} -- /bin/bash', pty=True)
