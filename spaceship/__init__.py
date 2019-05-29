from flask import Flask
from flask_assets import Environment, Bundle

app = Flask(__name__)
assets = Environment(app)

# If you need the HTML to include each JS file via its own <script> tag,
# uncomment this line:
# assets.debug = True

js = Bundle('edit.js',
            'prevent-invalid-form-submit.js',
            'wip-overlay.js',
            output='gen/all.%(version)s.js')
assets.register('js_all', js)

css = Bundle('spaceship.css',
             'wip-overlay.css',
             output='gen/all.%(version)s.css')
assets.register('css_all', css)

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

