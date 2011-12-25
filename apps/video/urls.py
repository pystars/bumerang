# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from apps.video.views import (VideoListView, VideoDetailView, upload_view,
    VideoCreateView, VideoAlbumCreateView, VideoAlbumDetailView)


urlpatterns = patterns('',
    url(r'^video-album/add/$',
        login_required(VideoAlbumCreateView.as_view()),
        name='video-album-add'
    ),
    url(r'^video-album(?P<video_album_id>[\d]+)/video/add/$',
        login_required(VideoCreateView.as_view()),
        name='video-add'
    ),
    url(r'^album(?P<pk>[\d]+)/$',
        VideoAlbumDetailView.as_view(),
        name='video-album-detail'
    ),
    url(r'^archive/$',
        VideoListView.as_view(),
        name='video-list'
    ),
    url(r'^(?P<pk>\w+)/$',
        VideoDetailView.as_view(),
        name='video-detail'
    ),
    url(r'^$',
        upload_view,
        name='VideoView'
    ),
)