from datascope.settings_base import *

DATABASES["default"]["ENGINE"] = 'django.db.backends.mysql'
DATABASES["default"]["NAME"] = 's52573__datascope'
DATABASES["default"]["USER"] = 's52573'
DATABASES["default"]["PASSWORD"] = MYSQL_PASSWORD
DATABASES["default"]["HOST"] = 'tools-db'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
STATIC_URL = "//tools-static.wmflabs.org/algo-news/static/"

CELERY_DEFAULT_QUEUE = 'datascope'
BROKER_URL = 'redis://tools-redis:6379/0'
MAX_BATCH_SIZE = 100

# TODO: add STATIC_IP
