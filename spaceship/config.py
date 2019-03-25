import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
  IN_PRODUCTION = bool(os.environ.get('IN_PRODUCTION', False))
  SECRET_KEY = os.environ.get('SECRET_KEY', 'develoment')

  MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1:9877')
  MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME', 'spaceship-app')
  MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'aa7925b6f7b')

  MYSQL_URL = ''.join([
      'mysql://',
      MYSQL_USERNAME,
      ':',
      MYSQL_PASSWORD,
      '@',
      MYSQL_HOST,
      '/spaceship',
    ])
