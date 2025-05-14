
from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = os.environ.get('SECRET_KEY')
#DEBUG = os.environ.get("DEBUG", "False") == "true"
#ALLOWED_HOSTS = os.environ.get("ALLOWED_HOST").split(" ")
SECRET_KEY = 'tR2KWjP-dIiazOaMz8Jc9QHjZUtVWGzbzvye8Aqo3mmwaLtR8NJ9TOFysu3SMoh5078'
DEBUG = True
ALLOWED_HOSTS = ['*','127.0.0.1:8000']
CSRF_TRUSTED_ORIGINS = [
    "https://cyberclash.onrender.com",  # Add your Render domain
]
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    # Add other hashers if needed
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' 
STATIC_ROOT = 'staticfiles'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Application definition
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'channels',
    'myapp',
]

MIDDLEWARE = [
     'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
     'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
TEMPLATES = [
     {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Add this if you have a global templates directory
        'APP_DIRS': True,  # Ensure this is True
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

OPENAI_API_KEY = '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'
WSGI_APPLICATION = 'myproject.wsgi.application'

ASGI_APPLICATION = 'myproject.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',  # For local dev, switch to Redis in production
    },
}
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.sqlite3',
       'NAME': BASE_DIR / 'db.sqlite3',
    }
}


#DATABASES["default"] = dj_database_url.parse('postgresql://cyberclash_r0cp_user:2pxHqk6Y0TxYZyD3vdzYp5XSQwYKvV2V@dpg-cuobqadds78s738ifbhg-a.oregon-postgres.render.com/cyberclash_r0cp')

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

MEDIA_URL = '/media/'  # URL to access media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'cyberclash.capstone@gmail.com'
EMAIL_HOST_PASSWORD = 'ktey rmca lgyk cqrq'



SITE_ID = 1

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Manila'
USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
