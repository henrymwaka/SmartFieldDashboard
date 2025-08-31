import os
from decouple import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Core
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)

# Hosts and CSRF
# Comma-separated for ALLOWED_HOSTS, space-separated for CSRF_TRUSTED_ORIGINS in .env
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,smartfield.reslab.dev'
).split(',')

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://smartfield.reslab.dev http://smartfield.reslab.dev'
).split()

# ---------------------------------------------------------------------
# ADDED: ODK-X base URL made available via settings for quick health checks
# This avoids KeyError when using manage.py shell and keeps behavior consistent
ODKX_SYNC_URL = config('ODKX_SYNC_URL', default='https://odkx.reslab.dev')
# ---------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dashboard',
    'rest_framework',
    'oauth2_provider',
    'drf_yasg',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
]

ROOT_URLCONF = 'smartfield_dashboard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'smartfield_dashboard.wsgi.application'

# ---------------------------------------------------------------------
# CHANGED: Database
# Keep SQLite for default, and add a read-only Postgres link named "odkx"
# This points to PG15 analytics on localhost:5433 as per your runbook
# Django reads env vars and never talks to ODK-X 9.6 directly
# ---------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'odkx': {  # ADDED secondary DB for analytics via FDW
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('ODKX_DB_NAME', default='postgres'),
        'USER': config('ODKX_DB_USER', default='smartfield_ro'),
        'PASSWORD': config('ODKX_DB_PASSWORD', default=''),
        'HOST': config('ODKX_DB_HOST', default='127.0.0.1'),
        'PORT': config('ODKX_DB_PORT', cast=int, default=5433),
        'CONN_MAX_AGE': 300,            # keep connections warm
        'CONN_HEALTH_CHECKS': True,     # verify connections on reuse
        'OPTIONS': {
            'options': '-c search_path=odkx,analytics,public'  # resolve unqualified names
        },
    },
}

# ---------------------------------------------------------------------
# ADDED: Router to block writes and migrations on the "odkx" database
# Ensure you have smartfield_dashboard/routers.py with ODKXReadOnlyRouter
# ---------------------------------------------------------------------
DATABASE_ROUTERS = ['smartfield_dashboard.routers.ODKXReadOnlyRouter']

# Static and media (unchanged)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Auth redirects (unchanged)
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Email (unchanged)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# DRF and OAuth2 (unchanged)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 36000,
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 600,
    'APPLICATION_MODEL': 'oauth2_provider.Application',
    'REFRESH_TOKEN_EXPIRE_SECONDS': 1209600,
}

# Reverse proxy and HTTPS awareness
# Nginx sets X-Forwarded-Proto to "https" for Cloudflare. This avoids
# contradictory scheme header errors and makes request.is_secure() correct.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# ---------------------------------------------------------------------
# NOTE: Do not enable SECURE_SSL_REDIRECT here unless you terminate TLS
# at the origin on :443. Keeping it off prevents redirect loops while
# you are proxying HTTP on :80 behind Cloudflare.
# ---------------------------------------------------------------------
# SECURE_SSL_REDIRECT = True  # leave commented until origin serves HTTPS

# Cookies: secure in prod, relaxed in dev
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
