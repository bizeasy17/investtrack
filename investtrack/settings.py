"""
Django settings for investtrack project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import tushare as ts

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0u6iuu7lq^s1%)!_ydabj-&hg!1&z72+5ei-@i*uyn7-r&0=ko'

# token settings (not sure should put it here)
ts.set_token('3ebfccf82c537f1e8010e97707393003c1d98b86907dfd09f9d17589')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = False  # True
DEBUG = True
ALLOWED_HOSTS = ['192.168.31.217', '127.0.0.1']
# 卖出股票的策略是先进先出FIFO，可选的其他策略有FILO
STOCK_OUT_STRATEGY = 'FIFO'

NEAREST_THRESHOLD = 0.1


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.forms',
    # 3rd Party Apps
    # 'mdeditor',
    'rest_framework',
    'easy_thumbnails',
    'crispy_forms',
    'tushare',
    # local application
    'siteadmins.apps.SiteadminsConfig',
    'users.apps.UsersConfig',
    # 'investmgr.apps.InvestmgrConfig',
    # 'notifications.apps.NotificationsConfig',
    # refact 1
    'stockmarket.apps.StockmarketConfig',
    # 'stocktrade.apps.StocktradeConfig',
    # 'tradeaccounts.apps.TradeaccountsConfig',
    'investors.apps.InvestorsConfig',
    # 'txnvisibility.apps.TxnvisibilityConfig',
    # 'dashboard.apps.DashboardConfig',
    'analysis.apps.AnalysisConfig',
    'search.apps.SearchConfig',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
    # ,
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 10
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # for internationalization
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'investtrack.urls'

# paginate
PAGINATE_BY = 10

# to avoid the /admin url can not be found error
SITE_ID = 1

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # 'allauth.account.auth_backends.AuthenticationBackend',
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = 'users.User'
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = 'account:login'
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = 'search:home'
LOGOUT_REDIRECT_URL = 'search:home'
# https://django-allauth.readthedocs.io/en/latest/configuration.html
# ACCOUNT_EMAIL_VERIFICATION = 'none'
# https://django-allauth.readthedocs.io/en/latest/configuration.html
# ACCOUNT_AUTHENTICATION_METHOD = 'username'
# https://django-allauth.readthedocs.io/en/latest/configuration.html
# ACCOUNT_ADAPTER = 'users.adapters.AccountAdapter'
# https://django-allauth.readthedocs.io/en/latest/configuration.html
# SOCIALACCOUNT_ADAPTER = 'users.adapters.SocialAccountAdapter'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # change the dir from the default templates dir under app into this dir
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

WSGI_APPLICATION = 'investtrack.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

# Change the database connection to postgresql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'investtrack',
        'USER': 'db_usr',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': 5432,
        'OPTIONS': {'client_encoding': 'UTF8'},
    }
}
# PROD
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'investtrack_prod',
#         'USER': 'db_user1',
#         'PASSWORD': 'password1!',
#         'HOST': '39.100.215.105',
#         'PORT': 5432,
#         'OPTIONS': {'client_encoding': 'UTF8'},
#     }
# }

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'log_file'],
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d %(module)s] %(message)s',
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'log_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '51touz_cn.log',
            'maxBytes': 16777216,  # 16 MB
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'djangoblog': {
            'handlers': ['log_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'  # use China timezone

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Django Markdown Editor confi
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'collectedstatic')

STATICFILES = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    str(os.path.abspath(os.path.join(BASE_DIR, './static'))),
    str(os.path.abspath(os.path.join(BASE_DIR, './uploads'))),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# For file upload
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
MEDIA_URL = '/media/'
