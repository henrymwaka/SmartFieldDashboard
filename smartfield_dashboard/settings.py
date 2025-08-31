import os
from decouple import config, Csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Core
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='127.0.0.1,localhost,10.70.25.72',
    cast=Csv()
)

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    # include scheme and port for each origin actually used
    default='http://10.70.25.72:8080',
    cast=Csv()
)

INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'dashboard','rest_framework','oauth2_provider','drf_yasg','django_extensions',
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

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'smartfield_dashboard.wsgi.application'

# --- Databases ---
# NOTE: 'odkx' points to PG15 analytics (FDW -> ODK-X PG9.6). Defaults match your working setup.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'odkx': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('ODKX_DB_NAME', default='postgres'),
        'USER': config('ODKX_DB_USER', default='smartfield_ro'),
        'PASSWORD': config('ODKX_DB_PASSWORD'),
        'HOST': config('ODKX_DB_HOST', default='127.0.0.1'),
        'PORT': config('ODKX_DB_PORT', cast=int, default=5433),
        'CONN_MAX_AGE': 300,            # keep PG15 connection warm for 5 minutes
        'CONN_HEALTH_CHECKS': True,     # ping on reuse
        'OPTIONS': {
            'options': '-c search_path=odkx,public',
            # 'sslmode': 'require',   # keep if you also need TLS
        },
        # 'OPTIONS': {'options': '-c search_path=odkx,public'},  # uncomment if you want unqualified table names to resolve to odkx schema
        # 'OPTIONS': {'sslmode': 'require'},                      # enable if PG15 uses TLS
    },
}

# Protect the ODK-X/FDW DB from writes via a router (file must exist)
DATABASE_ROUTERS = ['smartfield_dashboard.routers.ODKXReadOnlyRouter']

# Static/Media (served behind /smartfield)
STATIC_URL  = '/smartfield/static/'
STATIC_ROOT = r'/var/www/sfdash/static'
MEDIA_URL   = '/smartfield/media/'
MEDIA_ROOT  = r'/var/www/sfdash/media'

# Auth redirects
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# DRF / OAuth2
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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# App is mounted under /smartfield
FORCE_SCRIPT_NAME = '/smartfield'

DATABASE_ROUTERS = ['smartfield_dashboard.routers.ODKXReadOnlyRouter']
