from .base import *
import dj_database_url

DEBUG = True

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

STATICFILES_DIRS = []
static_path = os.path.join(BASE_DIR, 'find_pp2m', 'static')
if os.path.exists(static_path):
    STATICFILES_DIRS.append(static_path)