
from flask import request, redirect
from werkzeug.middleware.proxy_fix import ProxyFix

from . import app

# first, apply the proxy fix. this makes us be happy if we're behind
# a proxy and running over https (e.g., fixes url generation)
# we expect a single forward (from google ingress) so both `for` and `proto` are set to 1
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

# now, if we have a `X-Forwarded-Proto` field that's `http`, redirect to https
@app.before_request
def enforce_ssl():
  # assume https to avoid dev-mode redirects
  forwarded_proto = request.headers.get('X-Forwarded-Proto', 'https')
  if forwarded_proto == 'http':
    url = request.url.replace('http://', 'https://', 1)
    return redirect(url, 302)
