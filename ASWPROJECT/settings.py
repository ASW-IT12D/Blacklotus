"""
Django settings for ASWPROJECT project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path

import social_django.middleware

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8y@g%vwm%8hgatsrkscuy-grlx9&l-6b-3v=*@mcrh03tnw93p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'blacklotus',
    'social_django',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'ASWPROJECT.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
            ],
        },
    },
]
AUTHENTICATION_BACKENDS = [
    'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

SOCIAL_AUTH_GITHUB_KEY = 'f602b1295efdaf14b9b4'
SOCIAL_AUTH_GITHUB_SECRET = 'f5c0e921221a277318989f68c35f0927e863c701'

WSGI_APPLICATION = 'ASWPROJECT.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# AWS S3 Settings
AWS_ACCESS_KEY_ID = 'ASIAUOQ5NQL2TB2A664R'
AWS_SECRET_ACCESS_KEY = '1SckETEKS6OrzWfkemXQGlIxvvxgvqAiD7RSsWhN'
AWS_STORAGE_BUCKET_NAME = 'blacklotusbucket2'
AWS_S3_REGION_NAME = 'us-east-1'
AWS_SESSION_TOKEN = 'FwoGZXIvYXdzEO///////////wEaDGihLMJH0y5jThgaPiLXAS5j6VA8rtf+Xt+5/AGkLLR4Nxy5uFXl7wq2zMHQC02ix4Bno/U3/xh+xZPUN4lipmGUvRp4GtaeLnEdODnnQcqAdhYNo7+5+DUezWXbIxWbIlgY0icyzLhOroa2x+h8YyiXS04hZOdsqdQrR7g5wzW76fXw3ksdtf88tW82Xf0Rzyn3fdHwOv8yfo/qoX2RIPwMDtQi0dom/tDWufxWIEOjGEdTxcQR0Cp5+xXecURVwfN2z9cq7yPwQqyQ2n6mKCysuqyVlUlk4KbuI6fgCJ6u1fYFdaIgKIvilKIGMi0Q3UDW21d3rnvt9TTxNXMA5YlJvBvH58Yup50xopZv7DjtFxcUyMpnlF8EiPM='
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}