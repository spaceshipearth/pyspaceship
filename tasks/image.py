from invoke import task, run
from invoke.exceptions import Exit

import tempfile

from .utils import load_manifest, in_repo_root, K8SNamespace, TEST_NAMESPACE

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
  output = run('docker build -t %s .' % tag).stdout

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

def do_deploy(tag, ns):
  """actually perform a deploy of the manifests"""
  deployment = load_manifest(
    'deployment',
    {
      'image': tag,
    }
  )

  ns.apply(deployment)

  service = load_manifest('service')
  ns.apply(service)

@task(
  default=True,
  help={
    'version': "Proposed version for the release (default: hash of repo state)",
    'namespace': f"Namespace to release to (default: {TEST_NAMESPACE})",
  },
)
def release(ctx, version = None, namespace = TEST_NAMESPACE):
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
  with K8SNamespace(namespace) as ns:
    do_deploy(docker_tag, ns)

@task(
  help={
    'version': "The version part of the image tag (default: hash of repo state)",
    'push': "Push the image to GCR after building (default: True)",
  })
def build(ctx, version=None, push=True):
  """Builds and uploads the docker image (first part of `release`)"""
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
    'version': "Just the version part of the image tag",
    'namespace': f"Namespace to deploy into (default: {TEST_NAMESPACE}",
    'dry-run': "Display the configuration that would be applied",
  })
def deploy(ctx, version, namespace = TEST_NAMESPACE, dry_run = False):
  """Generates and applies k8s configuration (second part of `release`)"""
  tag = generate_tag(version)
  with K8SNamespace(namespace, dry_run) as ns:
    do_deploy(tag, ns)
