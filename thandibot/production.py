from .settings import *  # noqa
from os import environ

# Disable debug mode

DEBUG = False
ENV = 'prd'
TEMPLATE_DEBUG = False

SECRET_KEY = environ.get('SECRET_KEY') or 'please-change-me'
BASE_DIR = (
    environ.get('BASE_DIR') or BASE_DIR)

RAVEN_DSN = environ.get('RAVEN_DSN')
RAVEN_CONFIG = {'dsn': RAVEN_DSN} if RAVEN_DSN else {}

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
