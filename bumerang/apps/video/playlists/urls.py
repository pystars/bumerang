# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from views import PlaylistDetailView


urlpatterns = patterns('',
    url(r'^(?P<channel>\w+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        PlaylistDetailView.as_view(),
        name='playlist-detail'
    ),
)