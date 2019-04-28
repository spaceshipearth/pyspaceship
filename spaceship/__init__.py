from flask import Flask

# this is to make url_for() use https:// for _external urls (like oauth
# redirect_uri) when deployed behind a load-balancer that talks http
class ReverseProxied(object):
  def __init__(self, app):
    self.app = app

  def __call__(self, environ, start_response):
    scheme = environ.get('HTTP_X_FORWARDED_PROTO')
    if scheme:
      environ['wsgi.url_scheme'] = scheme
    return self.app(environ, start_response)

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

from .config import Config
app.config.from_object(Config)

from . import logs

from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

from . import enforce_ssl
from . import enforce_www
from . import google_auth
from . import db
from . import login
from . import views

