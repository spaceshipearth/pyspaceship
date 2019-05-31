from . import app
from flask_assets import Environment, Bundle

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
