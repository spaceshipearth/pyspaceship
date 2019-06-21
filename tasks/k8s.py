
from invoke import task, run
from invoke.exceptions import UnexpectedExit

import json

from tasks.utils import load_manifest, K8SNamespace, TEST_NAMESPACE, random_string

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

@task(
  help={
    'namespace': f'Name of the namespace to initialize (default: {TEST_NAMESPACE})',
  }
)
def namespace(ctx, namespace):
  """initializes a namespace, like a site version"""
  # create a db with a user for the namespace
  user = f"spaceship-{namespace}"
  try:
    run(f"gcloud sql databases create {user} --instance=spaceshipdb", hide=True)
    print(f"created db {user}")
  except UnexpectedExit as e:
    if 'database exists' in e.result.stderr:
      print(f'db {user} already existed')
    else:
      raise

  # create the namespace
  with K8SNamespace.prod() as prod:
    nsmanifest = load_manifest('namespace', {'namespace': namespace})
    prod.apply(nsmanifest)

  # create the db user and session secrets if they don't exist
  with K8SNamespace(namespace) as ns:
    existing = ns.get_secret('pyspaceship-mysql')
    if not existing:
      password = random_string(12)
      run(
        f"gcloud sql users create {user} --host='%' --instance=spaceshipdb --password={password}",
        hide=True
      )
      print(f'created db user {user}')
      mysql_secret(ctx, username=user, password=password, namespace=namespace, db=user)
    else:
      print('mysql user already initialized')

    exiting = ns.get_secret('pyspaceship-session')
    if not existing:
      session_secret(ctx, namespace=namespace)
    else:
      print('session already initialized')

  # copy the google and sendgrid secrets from prod
  for secret_name in ['pyspaceship-google-oauth', 'pyspaceship-sendgrid', 'google-app-creds']:
    with K8SNamespace.prod() as prod:
      data = prod.get_secret(secret_name)

    secret = load_manifest('generic_secret', {'name': secret_name, 'data': data})
    with K8SNamespace(namespace) as ns:
      ns.apply(secret)

  # create an ssl cert and ingress for the namespace
  with K8SNamespace(namespace) as ns:
    ssl_cert = load_manifest('cert', {'namespace': namespace})
    ns.apply(ssl_cert)

    ingress = load_manifest('ingress', {'namespace': namespace})
    ns.apply(ingress)

    info = json.loads(
      run(f'{ns.kubecmd} get ingress pyspaceship-ingress -o=json', hide=True).stdout)

    print("Load balancer IPs:")
    try:
      ingress = info['status']['loadBalancer']['ingress']
    except KeyError:
      print("None assigned (yet?) -- re-run later to get IP address")
    else:
      ips = set()
      for i in ingress:
        ip = i['ip']
        ips.add(ip)
        print(f'- {ip}')

      dns_name = f'{namespace}.spaceshipearth.org.'

      existing = set()
      existing_data = json.loads(
        run(
          f'gcloud dns record-sets list -z spaceshipearth-org --name "{dns_name}" --format json',
          hide=True
        ).stdout
      )
      for record in existing_data:
        for addr in record['rrdatas']:
          existing.add(addr)

      to_add = ips - existing
      if len(to_add) == 0:
        print('all ip addresses already in DNS')

      for addr in to_add:
        print(f'adding {addr} as an A record for {dns_name}')

        def dns_trans(cmd):
          base_cmd = 'gcloud dns record-sets transaction'
          suffix = '--zone spaceshipearth-org'
          return run(f"{base_cmd} {cmd} {suffix}", hide=True)

        dns_trans('start')
        dns_trans(f'add --name="{dns_name}" --type=A --ttl 300 "{addr}"')
        dns_trans('execute')


@task(
  help={
    'secret-name': "Name of the secret to output",
    'namespace': f"Version of the site (default: {TEST_NAMESPACE})",
  }
)
def show_secret(ctx, secret_name, namespace=TEST_NAMESPACE):
  """Displays the contents of a kubernetes secret"""
  with K8SNamespace(namespace) as ns:
    data = ns.get_secret(secret_name)
    print(json.dumps(data, indent=4))

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
    password,
    host='10.82.64.3',
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
