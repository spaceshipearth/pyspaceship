import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
  IN_PRODUCTION = bool(os.environ.get('IN_PRODUCTION', False))
  SECRET_KEY = os.environ.get('SECRET_KEY', 'develoment')
  SENDGRID_KEY = os.environ.get('SENDGRID_KEY', None)
  EMAIL_CONFIRM_SALT = 'email-confirm-salt'

  MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
  MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 9877))
  MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME', 'spaceship-app')
  MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'aa7925b6f7b')
  MYSQL_DB = os.environ.get('MYSQL_DB', 'spaceship')
