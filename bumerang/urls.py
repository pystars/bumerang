# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from filebrowser.sites import FileBrowserSite

from bumerang.apps.utils.media_storage import media_storage


site = FileBrowserSite(name='filebrowser', storage=media_storage)

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/django-ses/', include('django_ses.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),
    (r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^tinymce/', include('tinymce.urls')),
    url(r'^$', include('bumerang.apps.bumerang_site.urls')),
    url(r'^news/', include('bumerang.apps.news.urls')),
    url(r'^accounts/', include('bumerang.apps.accounts.urls')),
    url(r'^advices/', include('bumerang.apps.advices.urls')),
    url(r'^video/', include('bumerang.apps.video.urls')),
    url(r'^photo/', include('bumerang.apps.photo.urls')),
    url(r'^playlists/', include('bumerang.apps.video.playlists.urls')),
    url(r'^events/', include('bumerang.apps.events.urls')),
    url(r'^projects/', include('bumerang.apps.projects.urls')),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
