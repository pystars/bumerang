# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin
from filebrowser.sites import site

import settings


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^tinymce/', include('tinymce.urls')),

    url(r'^$', include('bumerang.apps.bumerang_site.urls')),
    url(r'^news/', include('bumerang.apps.news.urls')),
    url(r'^accounts/', include('bumerang.apps.accounts.urls')),
    url(r'^advices/', include('bumerang.apps.advices.urls')),
    url(r'^video/', include('bumerang.apps.video.urls')),
    url(r'^accounts/', include('bumerang.apps.accounts.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^media/(?P<path>.*)$', 'serve'),
    )
