# -*- coding: utf-8 -*-
DEBUG = False
import os
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'bumerang.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

try:
    from bumerang.local_settings import *
except ImportError:
    pass

TEMPLATE_DEBUG = DEBUG

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

ADMINS = [
    ('Iljin', 'alexei.iljin@gmail.com'),
    ('Bolshakov', 'va.bolshakov@gmail.com')
]

MANAGERS = ADMINS

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'ru-RU'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

#Storage settings
if LOCALHOST:
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
    STATIC_ROOT = os.path.join(PROJECT_ROOT, STATIC_URL[1:])
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, MEDIA_URL[1:])
else:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    MEDIA_ROOT = ''
    AWS_STORAGE_BUCKET_NAME = 'static.probumerang.tv'
    AWS_MEDIA_STORAGE_BUCKET_NAME = 'media.probumerang.tv'
    AWS_S3_SECURE_URLS = False
    AWS_PRELOAD_METADATA = True
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    MEDIA_URL = 'http://media.probumerang.tv.s3-website-eu-west-1.amazonaws.com/'
    STATIC_ROOT = ''
    STATIC_URL = 'http://static.probumerang.tv.s3-website-eu-west-1.amazonaws.com/'

FILE_UPLOAD_TEMP_DIR = '/tmp'
FILE_UPLOAD_PERMISSIONS = 0644

SUPPORTED_VIDEO_FORMATS = ['avi','mkv','vob','mp4','ogv','ogg','m4v','m2ts',
                       'mts','m2t','wmv','ogm','mov','qt','mpg','mpeg','mp4v']

STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'templates/static'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
]


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'bumerang.apps.accounts.context_processors.global_login_form',
    'bumerang.apps.messages.context_processors.inbox',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'bumerang.apps.accounts.middleware.KeepLoggedInMiddleware',
]

if DEBUG:
    MIDDLEWARE_CLASSES += ['bumerang.apps.utils.middleware.ProfilerMiddleware']

# Keep me logged settings
KEEP_LOGGED_KEY = 'keep_me_logged'
KEEP_LOGGED_DURATION = 30  # in days

# used this component:
# https://github.com/martinrusev/django-redis-sessions
#SESSION_ENGINE = 'redis_sessions.session'
#SESSION_REDIS_HOST = '10.0.0.10'
#SESSION_REDIS_PORT = 6379
#SESSION_REDIS_DB = 0
#SESSION_REDIS_PASSWORD = 'fr6kdrWqDlRu8kktHv4FzhlH4CgW3JPC'

ROOT_URLCONF = 'bumerang.urls'

TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, 'templates'),
]

AUTH_PROFILE_MODULE = 'bumerang.apps.accounts.models.Profile'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'sitetree',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    'grappelli',
#    'filebrowser',
    'django.contrib.admin',
    'django.contrib.admindocs',
    # external
    'south',
    'mptt',
    'tinymce',
    'djcelery',
    'storages',
    'djkombu',
    'djangoratings',
    'django_ses',
    'django_extensions',
    # internal
    'bumerang.apps.bumerang_site',
    'bumerang.apps.news',
    'bumerang.apps.advices',
    'bumerang.apps.video',
    'bumerang.apps.video.albums',
    'bumerang.apps.video.playlists',
    'bumerang.apps.video.converting',
    'bumerang.apps.photo',
    'bumerang.apps.photo.albums',
    'bumerang.apps.accounts',
    'bumerang.apps.utils',
    'bumerang.apps.messages',
]

MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

#TINYMCE_JS_URL = os.path.join(STATIC_ROOT, "tiny_mce/tiny_mce.js")
#TINYMCE_JS_ROOT = os.path.join(MEDIA_ROOT, "tiny_mce")

TINYMCE_PLUGINS = [
    'safari',
    'table',
    'advlink',
    'advimage',
    'iespell',
    'inlinepopups',
    'media',
    'searchreplace',
    'contextmenu',
    'paste',
    'wordcount'
]
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,paste,searchreplace",
    'theme': "advanced",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
    }

FILEBROWSER_DIRECTORY = 'uploads/'

GRAPPELLI_ADMIN_TITLE = u'Bumerang'

FIXTURE_DIRS = (
    os.path.join(PROJECT_ROOT, 'fixtures'),
)

PREVIEWS_COUNT = 5

if DEBUG:
    INSTALLED_APPS += ('debug_toolbar',)

    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
    )

    INTERNAL_IPS = ('127.0.0.1',)
    DEBUG_TOOLBAR_CONFIG = dict(
        INTERCEPT_REDIRECTS=False
    )

EMAIL_NOREPLY_ADDR = 'noreply@probumerang.tv'
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION_NAME = 'us-east-1'
AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'

import djcelery

#if LOCALHOST:
#    BROKER_TRANSPORT = 'djkombu.transport.DatabaseTransport'
#else:
#    BROKER_TRANSPORT = 'sqs'
#    BROKER_TRANSPORT_OPTIONS = {
#        'region': 'eu-west-1',
#    }
#    BROKER_USER = AWS_ACCESS_KEY_ID
#    BROKER_PASSWORD = AWS_SECRET_ACCESS_KEY
BROKER_POOL_LIMIT = 1
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
CELERY_RESULT_BACKEND = "database"

CELERY_DISABLE_RATE_LIMITS = True
CELERY_IGNORE_RESULT = True
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True
CELERYD_MAX_TASKS_PER_CHILD = 1
CELERYD_FORCE_EXECV = False
CELERYD_PREFETCH_MULTIPLIER = 1
#CELERY_SEND_TASK_ERROR_EMAILS = True
CELERYD_TASK_TIME_LIMIT = 86400
CELERY_DEFAULT_QUEUE = 'celery'
CELERY_QUEUES = {
    CELERY_DEFAULT_QUEUE : {
        'binding_key': CELERY_DEFAULT_QUEUE
    },
    'video': {
        'binding_key': 'video'
    }
}

djcelery.setup_loader()
