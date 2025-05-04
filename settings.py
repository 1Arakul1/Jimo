from pathlib import Path
import os
import sys  # Добавьте эту строку
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, os.path.join(BASE_DIR, 'dogs'))
sys.path.insert(0, os.path.join(BASE_DIR, 'users'))

# Load environment variables from .env file
load_dotenv()

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'e2mj4k7r9xgfvzwyuhqbdpci5n3tlsao681f0jesrm2qnxlopyy')
DEBUG = True  # В production должно быть False
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.1.2', '178.206.254.190']  # Замени на свой IP

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dogs',
    'users',
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'my_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Если есть общие шаблоны
            BASE_DIR / 'dogs' / 'templates' # Добавь этот путь!
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': True,  # Add this line
        },
    },
]

WSGI_APPLICATION = 'my_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv("DJANGO_DATABASE_NAME", "Bony"),
        'USER': os.getenv('DJANGO_DATABASE_USER'),
        'PASSWORD': os.getenv('DJANGO_DATABASE_PASSWORD'),
        'HOST': os.getenv('DJANGO_DATABASE_HOST'),
        'PORT': os.getenv('DJANGO_DATABASE_PORT', ''),
        'OPTIONS': {
            'driver': os.getenv('DJANGO_DATABASE_OPTIONS_DRIVER', 'ODBC Driver 17 for SQL Server'),
            'TrustServerCertificate': 'yes',
            'Encrypt': 'optional',
            'instance': os.getenv('DJANGO_DATABASE_OPTIONS_INSTANCE', 'SQLEXPRESS'),
        },
    }
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
TIME_ZONE = 'UTC'  # Или ваш часовой пояс, например 'Europe/Moscow'


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'  # Важно, чтобы начинался и заканчивался слэшем
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Убедись, что путь к твоим статическим файлам указан правильно
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Папка для сбора статики для продакшена

STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'  # URL для доступа к медиафайлам
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Путь к папке для сохранения медиафайлов

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'users:user_login'
LOGIN_REDIRECT_URL = 'dogs:index'
AUTH_USER_MODEL = 'users.User'
# settings.py

# settings.py

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'  # Хост Yandex.Mail
EMAIL_PORT = 465  # Порт для SSL (465) или 587 для TLS
EMAIL_USE_TLS = False #  Используйте False для SSL, True для TLS
EMAIL_USE_SSL = True # Используйте True для SSL, False для TLS
EMAIL_HOST_USER = 'niaz123rezeda123@ya.ru'  # Ваш адрес электронной почты Yandex
EMAIL_HOST_PASSWORD = 'qmcexvaqscmgaiey'  # Пароль от вашей почты Yandex
DEFAULT_FROM_EMAIL = 'niaz123rezeda123@ya.ru'  # От кого будут отправляться письма (ваш адрес)
DEFAULT_CHARSET = 'utf-8'  # или 'utf-8'
import logging
logger = logging.getLogger(__name__)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("CACHE_LOCATION", "redis://127.0.0.1:6379/0"),  #  Используйте переменную окружения для LOCATION
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": False, #  ИЗМЕНЕНО: Set to False for logging
             "SOCKET_TIMEOUT": 1,  # 1 second timeout
        }
    }
}
try:
    from django.core.cache import cache
    cache.get('test_cache_connection')
except Exception as e:
    logger.error(f"Redis connection error: {e}")
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',  # Замените на нужный путь
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
        },
         '': {  # Root logger
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
        },
    },
}
# Настройки кэширования (дополнительно)
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"  # Читаем из .env
CACHE_MIDDLEWARE_ALIAS = "default"  # Используем кэш по умолчанию
CACHE_MIDDLEWARE_SECONDS = 600  # 10 минут (время жизни кэша)
CACHE_MIDDLEWARE_KEY_PREFIX = ""  # Префикс для ключей кэша