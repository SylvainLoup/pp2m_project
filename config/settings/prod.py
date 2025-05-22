from .base import *
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}

# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_ROOT = '/opt/render/project/src/staticfiles'
STATIC_URL = '/static/'
print(STATIC_ROOT)