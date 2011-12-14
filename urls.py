# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from filebrowser.sites import site

import settings


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^tinymce/', include('tinymce.urls')),

    url(r'^$', include('apps.bumerang_site.urls')),
    url(r'^news/', include('apps.news.urls')),
    url(r'^advices/', include('apps.advices.urls')),
    #url(r'^video/', include('apps.video.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^media/(?P<path>.*)$', 'serve'),
    )
