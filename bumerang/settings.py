# -*- coding: utf-8 -*-
import os

import djcelery
from configurations import Settings

djcelery.setup_loader()


class CommonSettings(Settings):

    DEBUG = False
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'bumerang.db',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        },
    }

    TEMPLATE_DEBUG = DEBUG

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    ADMINS = [
        ('Iljin', 'alexei.iljin@gmail.com'),
        ('Bolshakov', 'va.bolshakov@gmail.com'),
        ('Dashkov', 'dashkov.a@mail.ru')
    ]

    MANAGERS = ADMINS

    SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
    TIME_ZONE = 'Europe/Moscow'
    LANGUAGE_CODE = 'ru-RU'
    SITE_ID = 1
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    PLAYLIST_START_TIME_SHIFT = {'days': -1, 'hours': 23}

    #Storage settings
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, MEDIA_URL[1:])
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(PROJECT_ROOT, STATIC_URL[1:])


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
        # bumerang - specific ctx processors
        'bumerang.apps.accounts.context_processors.global_login_form',
    ]

    MIDDLEWARE_CLASSES = [
    #    'johnny.middleware.LocalStoreClearMiddleware',
    #    'johnny.middleware.QueryCacheMiddleware',

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
        'sitetree',
        'django.contrib.flatpages',
        'django.contrib.staticfiles',
        'grappelli',
        'filebrowser',
        'django.contrib.admin',
        'django.contrib.admindocs',
        # external
        'tinymce',
        'south',
        'mptt',
        'djcelery',
        'storages',
        'djkombu',
        'django_ses',
    #    'django_wysiwyg',
        'django_extensions',
        'django_coverage',
        # we have two messages in project, so they must be in this order =\
        'bumerang.apps.messages',
        'django.contrib.messages',

        # internal
        'bumerang.apps.accounts',
        'bumerang.apps.news',
        'bumerang.apps.advices',
        'bumerang.apps.bumerang_site',
        'bumerang.apps.video',
        'bumerang.apps.photo',
        'bumerang.apps.video.albums',
        'bumerang.apps.video.playlists',
        'bumerang.apps.video.converting',
        'bumerang.apps.photo.albums',
        'bumerang.apps.utils',
        'bumerang.apps.events'
    ]

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            }
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
                },
            }
    }

    TINYMCE_JS_URL = "http://www.probumerang.tv/static/tiny_mce/tiny_mce.js"
    TINYMCE_JS_ROOT = STATIC_ROOT + "/tiny_mce"
    TINYMCE_SPELLCHECKER=False
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

    TINYMCE_DEFAULT_CONFIG={
        'theme' : "advanced",
        'plugins' : ",".join(TINYMCE_PLUGINS), # django-cms
        'language' : 'ru',
        'theme_advanced_buttons1' : "bullist,numlist,|,link,unlink,anchor,image",
        'theme_advanced_buttons3' : "table,|,delete_row,delete_table,|,row_after,row_before",
        'theme_advanced_buttons4' : "styleselect,formatselect,fontselect,fontsizeselect",
        'theme_advanced_buttons2' : "cut,copy,paste,pastetext,pasteword,|,search,replace,|,undo,redo,|,link,unlink,cleanup",
#        'theme_advanced_buttons4' : "",
        'theme_advanced_toolbar_location' : "top",
        'theme_advanced_toolbar_align' : "left",
        'theme_advanced_statusbar_location' : "bottom",
        'theme_advanced_resizing' : True,
        'table_default_cellpadding': 2,
        'table_default_cellspacing': 2,
        'cleanup_on_startup' : False,
        'cleanup' : False,
        'paste_auto_cleanup_on_paste' : False,
        'paste_block_drop' : False,
        'paste_remove_spans' : False,
        'paste_strip_class_attributes' : False,
        'paste_retain_style_properties' : "",
        'forced_root_block' : False,
        'force_br_newlines' : False,
        'force_p_newlines' : False,
        'remove_linebreaks' : False,
        'convert_newlines_to_brs' : False,
        'inline_styles' : False,
        'relative_urls' : False,
        'formats' : {
            'alignleft' : {'selector' : 'p,h1,h2,h3,h4,h5,h6,td,th,div,ul,ol,li,table,img', 'classes' : 'align-left'},
            'aligncenter' : {'selector' : 'p,h1,h2,h3,h4,h5,h6,td,th,div,ul,ol,li,table,img', 'classes' : 'align-center'},
            'alignright' : {'selector' : 'p,h1,h2,h3,h4,h5,h6,td,th,div,ul,ol,li,table,img', 'classes' : 'align-right'},
            'alignfull' : {'selector' : 'p,h1,h2,h3,h4,h5,h6,td,th,div,ul,ol,li,table,img', 'classes' : 'align-justify'},
            'strikethrough' : {'inline' : 'del'},
            'italic' : {'inline' : 'em'},
            'bold' : {'inline' : 'strong'},
            'underline' : {'inline' : 'u'}
        },
        'pagebreak_separator' : ""
    }

    MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

    DJANGO_WYSIWYG_FLAVOR = "ckeditor"

    FIXTURE_DIRS = (
        os.path.join(PROJECT_ROOT, 'fixtures'),
    )

    PREVIEWS_COUNT = 5

    EMAIL_NOREPLY_ADDR = 'noreply@probumerang.tv'
    EMAIL_BACKEND = 'django_ses.SESBackend'
    AWS_SES_REGION_NAME = 'us-east-1'
    AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'


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


try:
    from bumerang.local_settings import *
except ImportError:
    class LocalSettingsMixin(object):
        pass

class BumerSettings(LocalSettingsMixin, S3StaticMixin, CommonSettings):

    @property
    def INSTALLED_APPS(self):
        if self.DEBUG:
            return super(BumerSettings, self).INSTALLED_APPS + ['debug_toolbar']
        return super(BumerSettings, self).INSTALLED_APPS

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

    COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(
        CommonSettings.PROJECT_ROOT, 'coverage')


class AdminSettings(LocalSettingsMixin, CommonSettings):
    DEBUG = True
