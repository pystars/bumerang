# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from apps.video.views import VideoListView, VideoDetailView, upload_view, VideoCreateView


urlpatterns = patterns('',
    url(r'^archive/$', VideoListView.as_view(), name='video-list'),
    url(r'^add/$', login_required(VideoCreateView.as_view()), name='video-add'),
    url(r'^(?P<slug>\w+)/$', VideoDetailView.as_view(), name='video-detail'),
    url(r'^$', upload_view, name='VideoView'),
)