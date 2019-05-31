import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
  IN_BUILD = bool(os.environ.get('IN_BUILD', False))
  IN_PRODUCTION = bool(os.environ.get('IN_PRODUCTION', False))
  SECRET_KEY = os.environ.get('SECRET_KEY', 'develoment')
  SENDGRID_KEY = os.environ.get('SENDGRID_KEY', None)
  EMAIL_CONFIRM_SALT = 'email-confirm-salt'

  MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
  MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 9877))
  MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME', 'spaceship-app')
  MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'aa7925b6f7b')
  MYSQL_DB = os.environ.get('MYSQL_DB', 'spaceship')

  GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '700492634886-qbhv3gss1a59lm5p93gr7plo872auaba.apps.googleusercontent.com')
  GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'c1PSnZoSuVTOtta-g-OH_3ZL')
