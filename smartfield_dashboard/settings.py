from decouple import config
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',  # ← THIS IS MISSING!
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # your apps...
    'dashboard',  # or whatever your app is called
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
ROOT_URLCONF = 'smartfield_dashboard.urls'
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Ensure BASE_DIR is defined
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Optional: add your custom template dirs
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
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # REQUIRED for admin & sessions
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # REQUIRED
    'django.contrib.messages.middleware.MessageMiddleware',  # REQUIRED
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
STATIC_URL = '/static/'
SECRET_KEY = config('SECRET_KEY')
print("EMAIL_HOST:", EMAIL_HOST)
print("EMAIL_HOST_USER:", EMAIL_HOST_USER)
print("EMAIL_HOST_PASSWORD:", EMAIL_HOST_PASSWORD)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DEBUG = True
ALLOWED_HOSTS = ['*']

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
