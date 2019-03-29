from invoke import task, run
from invoke.exceptions import Exit

import json

from . import utils

DEFAULT_VERSION = 'latest'
REPO = "us.gcr.io"
PROJECT = "spaceshipearthprod"

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

@task(
  default=True,
  help={
    'version': "The version part of the image tag (default: '%s')" % DEFAULT_VERSION,
    'push': "Push the image to GCR after building (default: True)",
  })
def build(ctx, version=DEFAULT_VERSION, push=True):
  """Builds and uploads the docker image"""
  tag = generate_tag(version)

  result = do_build(tag)
  if push:
    do_push(tag)

  print('Built image %(image_id)s, tagged %(tag)s (context size: %(context_size)s)' % result)

@task(
  help={
    'version': "Proposed version for the release (e.g. 'v0.0.3')",
  })
def release(ctx, version):
  """Tags a release version in git and pushes a tagged docker image"""
  # sanity check on the specified version
  if not (version.startswith('v') and len(version.split('.')) == 3):
    raise Exit("Specified version %s doesn't look valid; it should look like this: `v1.2.3`")

  # pull to get the latest list of existing tags
  run('git fetch --tags')

  # check for tag conflicts
  existing_git_tags = run('git tag --list', hide=True).stdout.split('\n')
  if version in existing_git_tags:
    raise Exit("There is already a commit tagged with version %s -- use a later version!" % version)

  # generate and push correctly-tagged build
  docker_tag = generate_tag(version)
  do_build(docker_tag)
  do_push(docker_tag)

  # mark the git repo as corresponding to that tag
  run('git tag -a %s -m "Releasing image %s"' % (version, docker_tag))
  run('git push --tags')

@task(
  help={
    'version': "Just the version part of the image tag (default: '%s')" % DEFAULT_VERSION,
    'dry-run': "Just display the configuration to apply without invoking kubectl",
  })
def deploy(ctx, version = DEFAULT_VERSION, dry_run = False):
  """Generates and applies k8s configuration"""
  tag = generate_tag(version)

  deployment = utils.load_manifest(
    'deployment',
    {
      'image': tag,
    }
  )
  utils.k8s_apply(deployment, dry_run)

  service = utils.load_manifest('service')
  utils.k8s_apply(service, dry_run)

  ingress = utils.load_manifest('ingress')
  utils.k8s_apply(ingress, dry_run)

  info = json.loads(run('kubectl get ingress pyspaceship-ingress -o=json', hide=True).stdout)
  ingress = info['status']['loadBalancer']['ingress']
  print("Load balancer IPs:")
  for i in ingress:
    ip = i['ip']
    print(f'- {ip}')
