
from invoke import run

import contextlib
import json
import jsone
import os, os.path
import tempfile
import yaml

ROOT_REPO_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

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

def k8s_apply(manifest, dry_run = True):
  """run `kubectl apply` on the specified manifest"""
  # write out the modified config
  with tempfile.NamedTemporaryFile(mode='w') as tf:
    yaml.dump(manifest, tf)
    tf.flush()

    if dry_run:
      print("The config we generated:")
      print(open(tf.name).read())
      run('kubectl apply --dry-run -f %s' % tf.name)

    else:
      run('kubectl apply -f %s' % tf.name)

def get_pods():
  """List running pods"""
  items = json.loads(
    run('kubectl get pods -l app=pyspaceship -o=json', hide=True).stdout
  )['items']

  pods = []
  for item in items:
    pods.append({
      'name': item['metadata']['name'],
      'image': item['status']['containerStatuses'][0]['image'],
      'phase': item['status']['phase'],
    })

  return pods

def random_pod_name():
  return [p['name'] for p in get_pods() if p['phase'] == 'Running'].pop()

