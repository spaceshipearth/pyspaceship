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

Add the following to your `~/.bash_profile`

```
PYENV_VIRTUALENVWRAPPER_PREFER_PYVENV="true"
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

## MySQL ##

This app expects a MySQL database on port 9877.
If you have `docker-compose` set up, you can bring one up like so:

```
$ inv run.mysql
```

### Migrations ###

First, you need to create the migration.
You can do this through `migration-prep`:

```
$ inv run.migration-prep --name "my migration description"
```

This will generate your migration in `migrations/versions`.
You should edit this migration and commit it to the git repo.

Next, you can run your migration:

```
$ inv run.upgrade
```

If you need to back down again, run `inv run.downgrade`.


## In production ##

You need `kubectl` set up to talk to our K8S cluster.
You might need the following:

```bash
$ gcloud components install kubectl
$ gcloud container clusters get-credentials default --region us-central1-a
$ gcloud auth configure-docker
```

Run this just to make sure you're set up to talk to the cluster:

```bash
$ kubectl get nodes
```

### Building an image ###

Run `inv image.build`

### Manual steps in production ###

You have to do these by hand:
* set up a mysql database
  * give it a `spaceship-app` account
  * create a `spaceship` database
* create an ssl cert
