from . import app
from flask_assets import Environment, Bundle

assets = Environment(app)

if app.config['IN_BUILD']:
    assets.auto_build = False
    assets.cache = False
    assets.manifest = 'file'

js = Bundle('compose_email.js',
            'edit.js',
            'prevent-invalid-form-submit.js',
            'wip-overlay.js',
            output='gen/all.%(version)s.js')
assets.register('js_all', js)

css = Bundle('spaceship.css',
             'wip-overlay.css',
             output='gen/all.%(version)s.css')
assets.register('css_all', css)
