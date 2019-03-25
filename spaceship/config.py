import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
  IN_PRODUCTION = bool(os.environ.get('IN_PRODUCTION', False))
  SECRET_KEY = os.environ.get('SECRET_KEY', 'develoment')
