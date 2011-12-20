# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

from apps.video.views import VideoListView, VideoDetailView, upload_view

urlpatterns = patterns('',
    url(r'^archive/$', VideoListView.as_view(), name='video-list'),
    url(r'^(?P<slug>\w+)/$', VideoDetailView.as_view(), name='video-detail'),
    url(r'^$', upload_view, name='VideoView'),
)