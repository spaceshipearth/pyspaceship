
from invoke import run
from invoke.exceptions import UnexpectedExit

import base64
import contextlib
import json
import jsone
import os, os.path
import random
import string
import tempfile
import yaml

ROOT_REPO_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

DEFAULT_NAMESPACE = 'default'
TEST_NAMESPACE = 'test'
PROD_NAMESPACE = 'prod'

class K8SNamespace:
  def __init__(self, namespace, dry_run = False):
    self.namespace = namespace
    self.dry_run = dry_run

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    self.namespace = None

  def get_pods(self):
    """List running pods"""
    items = json.loads(
      run(f'{self.kubecmd} get pods -l app=pyspaceship -o=json', hide=True).stdout
    )['items']

    pods = []
    for item in items:
      pods.append({
        'name': item['metadata']['name'],
        'image': item['status']['containerStatuses'][0]['image'],
        'phase': item['status']['phase'],
      })

    return pods

  def random_pod_name(self):
    return [p['name'] for p in self.get_pods() if p['phase'] == 'Running'].pop()

  @property
  def kubecmd(self):
    return f"kubectl --namespace={self.namespace}"

  def get_secret(self, secret_name):
    try:
      secret = json.loads(
        run(f'{self.kubecmd} get secret {secret_name} -o json', hide=True).stdout)
    except UnexpectedExit as e:
      if 'not found' in e.result.stderr:
        return None
      else:
        raise

    data = {}
    for key, val in secret['data'].items():
      data[key] = base64.b64decode(val).decode('utf-8')

    return data


  def apply(self, manifest):
    """run `kubectl apply` on the specified manifest"""
    # write out the modified config
    with tempfile.NamedTemporaryFile(mode='w') as tf:
      yaml.dump(manifest, tf)
      tf.flush()

      if self.dry_run:
        print("The config we generated:")
        print(open(tf.name).read())
        run(f'{self.kubecmd} apply --dry-run -f {tf.name}')

      else:
        run(f'{self.kubecmd} apply -f {tf.name}')


@contextlib.contextmanager
def in_repo_root():
  cwd = os.getcwd()

  os.chdir(ROOT_REPO_DIR)
  try:
    yield
  finally:
    os.chdir(cwd)

def load_manifest(mtype, context = {}):
  """Load the specified yaml file given the specified context"""
  filename = f'{mtype}.yaml'
  manifest_path = os.path.join(ROOT_REPO_DIR, 'k8s', filename)

  with open(manifest_path) as mt:
    manifest_template = yaml.safe_load(mt.read())
    return jsone.render(manifest_template, context)

def random_string(length):
  return "".join( random.SystemRandom().choices(string.ascii_letters + string.digits, k=length))


