"""
Django settings for HimigTube project. YouTube to MP3 Project
AUTHOR: THE REAL DON
"""

from pathlib import Path
import os
import dj_database_url  # ✅ For PostgreSQL support on Render

# 📁 Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# 🚨 SECURITY SETTINGS
SECRET_KEY = 'u9-nhe%w41$#iqc&a&sv%xtunspr_+tk&l36gqnh1mckf638r0'
DEBUG = True
ALLOWED_HOSTS = ['himigtube.onrender.com', 'localhost', '127.0.0.1', '192.168.0.252']

# ✅ Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'converter',
]

# 🌐 Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ Required for static files on Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 🌐 URL & WSGI
ROOT_URLCONF = 'himigtube.urls'
WSGI_APPLICATION = 'himigtube.wsgi.application'

# 🖼 Template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# 🗃 Database (uses SQLite locally, PostgreSQL on Render)
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}", conn_max_age=600
    )
}

# 🔐 Password validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 🌍 Localization
LANGUAGE_CODE = 'en-ph'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

# 🧾 Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'converter' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ✅ Required to serve static files properly in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 🖼 Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 🔑 Default primary key type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
