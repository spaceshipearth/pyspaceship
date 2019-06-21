
from flask import request, redirect

from spaceship import app

# if we are on just `spaceshipearth.org` send to `www`
@app.before_request
def enforce_ssl():
  if request.host == 'spaceshipearth.org':
    url = request.url.replace('spaceshipearth.org', 'www.spaceshipearth.org', 1)
    return redirect(url, 302)
