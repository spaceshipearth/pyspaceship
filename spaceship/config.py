import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
  IN_BUILD = bool(os.environ.get('IN_BUILD', False))
  IN_PRODUCTION = bool(os.environ.get('IN_PRODUCTION', False))
  COMPONENT = os.environ.get('COMPONENT', 'unknown')

  SECRET_KEY = os.environ.get('SECRET_KEY', 'develoment')
  SENDGRID_KEY = os.environ.get('SENDGRID_KEY', None)
  EMAIL_CONFIRM_SALT = 'email-confirm-salt'

  MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
  MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 9877))
  MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME', 'spaceship-app')
  MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'aa7925b6f7b')
  MYSQL_DB = os.environ.get('MYSQL_DB', 'spaceship')

  SQLALCHEMY_DATABASE_URI = ''.join((
    'mysql+pymysql://',
    MYSQL_USERNAME,
    ':',
    MYSQL_PASSWORD,
    '@',
    MYSQL_HOST,
    ':',
    str(MYSQL_PORT),
    '/',
    MYSQL_DB,
  ))

  SQLALCHEMY_ECHO = True if not IN_PRODUCTION else False
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
  REDIS_PORT = int(os.environ.get('REDIS_PORT', 9878))
  REDIS_DB = int(os.environ.get('REDIS_DB', 0))

  GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '700492634886-qbhv3gss1a59lm5p93gr7plo872auaba.apps.googleusercontent.com')
  GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'c1PSnZoSuVTOtta-g-OH_3ZL')

  USE_CELERY_WORKERS = bool(int(os.environ.get('USE_CELERY_WORKERS', '0')))
  SERVER_NAME =  os.environ.get('SERVER_NAME', "localhost:9876")
  PREFERRED_URL_SCHEME = 'https' if IN_PRODUCTION else 'http'
