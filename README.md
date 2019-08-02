# PySpaceship #

A python implementation of [Spaceship Earth](python.spaceshipearth.org).

## Installation ##

We are expecting that you already have `pyenv` and `pyenv-virtualenvwrapper` installed.
If you haven't done that already, see how Igor does it in [his dotfiles](https://github.com/igor47/dotfiles/blob/264092d5314e3a83039554731a62c77ecd7d62ce/bashrc#L254-L270).

### If you are on a Mac

Install Homebrew

```
brew install pyenv
brew install pyenv-virtualenvwrapper
```

Add the following to your shell initialization config (e.g. `~/.bash_profile`, `~/.zshrc`, etc.)

```
export PYENV_VIRTUALENVWRAPPER_PREFER_PYVENV="true"
if command -v pyenv 1>/dev/null 2>&1
then
  eval "$(pyenv init -)"
  pyenv virtualenvwrapper
fi
```

Run the following to install a couple Python versions:
```
pyenv install 2.7.14
pyenv install 3.7.2

# If you are on macOS Mojave, you may get an error about zlib being missing.
# There are two ways to deal with this. You only need to do one of them. For
# details, see https://github.com/pyenv/pyenv/issues/1219.

# OPTION 1: Install the macOS SDK headers
# First install the Xcode Command Line Tools if you haven't already:
xcode-select --install
# Then install the headers:
sudo installer -pkg /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg -target /
# Then re-run the `pyenv install` commands.

# OPTION 2: When you run the `pyenv install` commands, set `CFLAGS` like so:
CFLAGS="-I$(xcrun --show-sdk-path)/usr/include" pyenv install ...
```

From the project directory, run the following command:
```
cp .python-version ~
```

Follow these instructions to get Docker up and running: https://stackoverflow.com/a/43365425


### Set up virtualenv

Create the virtualenv:

```
$ mkvirtualenv pyspaceship
```

Then, install some basic tooling:

```
$ pip install -r requirements.txt
```

Now, you can see all the tasks we have defined:

```
$ inv --list
```

## Running Locally ##

Run the website like so:

```
$ inv run.flask
```

To run via the gunicorn server, you can do:

```
$ inv run.gunicorn
```

The site will be accessible on localhost port 9876 (it's a countdown!).

The full sequence of commands to start running a local version of the site:
```
workon pyspaceship
pip install -r requirements.txt
inv run.mysql
inv run.upgrade
inv run.flask
```

## Sending email locally ## 

Create a file called sendgrid.key and place the sendgrid secret inside on a single line by itself.
You should also run
```
$ inv run.celery-worker
```

## MySQL ##

This app expects a MySQL database on port 9877.
If you have `docker-compose` set up, you can bring one up like so:

```
$ inv run.mysql
```

You can also connect to the mysql client like this:
```
$ inv run.mysql-client
```


### Migrations ###

First, you need to create the migration.
You can do this through `migration-prep`:

```
$ inv run.prep-migration --desc "my migration description"
```

This will generate your migration in `migrations/versions`.
You should edit this migration and commit it to the git repo.

Next, you can run your migration:

```
$ inv run.upgrade
```

If you need to back down again, run `inv run.downgrade`.

## Deploying

First ask someone (probably Igor S.) to add you to the Google Cloud team.

Then install the `gcloud` command-line tool. On macOS, you can do this:

```bash
$ brew cask install google-cloud-sdk
```

Then configure shtuff:

```bash
$ gcloud init

# Log in with your Google credentials, then choose the spaceshipearthprod project.
# If asked to set a default Compute Region and Zone, you can choose
# us-central1-a or just not choose one.

$ gcloud components install kubectl
$ gcloud container clusters get-credentials default --region us-central1-a
$ gcloud auth configure-docker
```

Run this just to make sure you're set up to talk to the cluster:

```bash
$ kubectl get nodes
```

You should see something like this:

```
NAME                                     STATUS    ROLES     AGE       VERSION
gke-default-default-pool-a7d246e3-0sg6   Ready     <none>    63d       v1.12.5-gke.5
gke-default-default-pool-a7d246e3-c432   Ready     <none>    32d       v1.12.5-gke.5
gke-default-default-pool-a7d246e3-q80g   Ready     <none>    32d       v1.12.5-gke.5
```

### Deploying to test

To deploy to the test environment:

    inv image

See results at https://test.spaceshipearth.org

### Deploying to production

    inv image --namespace prod

### Manual steps in production ###

You have to do these by hand:
* set up a mysql database
  * give it a `spaceship-app` account
  * create a `spaceship` database
* create an ssl cert
