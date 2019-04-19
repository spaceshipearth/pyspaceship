from invoke import task, run
from invoke.exceptions import Exit

import json
import tempfile

from .utils import load_manifest, k8s_apply, in_repo_root

DEFAULT_VERSION = 'latest'
REPO = "us.gcr.io"
PROJECT = "spaceshipearthprod"

def get_hash():
  """Gets a hash of the current state of the git repo, including uncommitted changes

  this is based on the answer here: https://stackoverflow.com/a/48213033/153995
  """
  with tempfile.NamedTemporaryFile() as tf:
    with in_repo_root():
      # copy the index to temporary file
      run(f'cp .git/index {tf.name}', hide=True)

      # environment uses the temporary file as the git index
      env = {'GIT_INDEX_FILE': tf.name}

      # return a hash of the state of the repo
      run('git add -u', hide=True, env=env)
      return run('git write-tree', hide=True, env=env).stdout.strip()

def generate_tag(version):
  """Generates a tag string for the docker image"""
  return f"{REPO}/{PROJECT}/pyspaceship:{version}"

def do_build(tag):
  """Builds the docker image"""
  print("Starting docker build...")
  output = run('docker build -t %s .' % tag, hide=True).stdout

  result = {
    'context_size': None,
    'image_id': None,
    'tag': tag,
  }

  for line in output.split('\n'):
    if line.startswith('Sending build context'):
      result['context_size'] = line.split()[-1]
    elif line.startswith('Successfully built'):
      result['image_id'] = line.split()[2]

  return result

def do_push(tag):
  """Actually pushes to the repo"""
  print(f"Pushing docker tag {tag}...")
  run('docker push %s' % tag)

def do_deploy(tag, dry_run = False):
  """actually perform a deploy of the manifests"""
  deployment = load_manifest(
    'deployment',
    {
      'image': tag,
    }
  )
  k8s_apply(deployment, dry_run)

  service = load_manifest('service')
  k8s_apply(service, dry_run)

  ingress = load_manifest('ingress')
  k8s_apply(ingress, dry_run)

  info = json.loads(run('kubectl get ingress pyspaceship-ingress -o=json', hide=True).stdout)
  ingress = info['status']['loadBalancer']['ingress']
  print("Load balancer IPs:")
  for i in ingress:
    ip = i['ip']
    print(f'- {ip}')

@task(
  default=True,
  help={
    'version': "Proposed version for the release (default: hash of repo state)",
  },
)
def release(ctx, version = None):
  """Releases a new version of the site"""
  # default to a hash of the repo state
  if not version:
    version = get_hash()
    print(f"pushing image using version {version}")

  # sanity check on the specified version
  if not (version.startswith('v') and len(version.split('.')) == 3):
    print(f"Specified version {version} doesn't look production-y (like, 'v1.2.3'), so skipping git tagging")
    do_tag = False
  else:
    do_tag = True

    # pull to get the latest list of existing tags
    run('git fetch --tags')

    # check for tag conflicts
    existing_git_tags = run('git tag --list', hide=True).stdout.split('\n')
    if version in existing_git_tags:
      raise Exit("There is already a commit tagged with version %s -- use a later version!" % version)

  # generate and push correctly-tagged build
  docker_tag = generate_tag(version)
  with in_repo_root():
    do_build(docker_tag)
    do_push(docker_tag)

  # mark the git repo as corresponding to that tag
  if do_tag:
    run('git tag -a %s -m "Releasing image %s"' % (version, docker_tag))
    run('git push --tags')

  # do the deploy
  do_deploy(docker_tag)

@task(
  help={
    'version': "The version part of the image tag (default: hash of repo state)",
    'push': "Push the image to GCR after building (default: True)",
  })
def build(ctx, version=None, push=True):
  """Builds and uploads the docker image"""
  # default to a hash of the repo state
  if not version:
    version = get_hash()
    print(f"pushing image using version {version}")

  # generate a tag from the version
  tag = generate_tag(version)

  with in_repo_root():
    result = do_build(tag)
    if push:
      do_push(tag)

  print('Built image %(image_id)s, tagged %(tag)s (context size: %(context_size)s)' % result)

@task(
  help={
    'version': "Just the version part of the image tag (default: '%s')" % DEFAULT_VERSION,
    'dry-run': "Just display the configuration to apply without invoking kubectl",
  })
def deploy(ctx, version = DEFAULT_VERSION, dry_run = False):
  """Generates and applies k8s configuration"""
  tag = generate_tag(version)
  do_deploy(tag)
