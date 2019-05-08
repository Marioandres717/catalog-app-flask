import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'store.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_COOKIE_SECURE = False  # change this to true in prod
    JWT_COOKIE_CRSF_PROTECT = True
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET')
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    JWT_SESSION_COOKIE = 3600
    JWT_COOKIE_DOMAIN = os.environ.get('JWT_COOKIE_DOMAIN') or None
