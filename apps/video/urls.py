# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView

from apps.video.models import Video, VideoAlbum
from apps.video.views import (VideoListView, upload_view,
    VideoCreateView, VideoAlbumCreateView, VideoDeleteView, VideosDeleteView,
    VideoUpdateView, VideoMoveView, VideoAlbumUpdateView)


urlpatterns = patterns('',
    url(r'^video-album/add/$',
        login_required(VideoAlbumCreateView.as_view()),
        name='video-album-add'
    ),
    url(r'^album(?P<video_album_id>[\d]+)/add/$',
        login_required(VideoCreateView.as_view()),
        name='album-video-add'
    ),
    url(r'^album(?P<pk>[\d]+)/$',
        DetailView.as_view(model=VideoAlbum),
        name='video-album-detail'
    ),
    url(r'^album(?P<pk>[\d]+)/edit/$',
        login_required(VideoAlbumUpdateView.as_view()),
        name='video-album-edit'
    ),
    url(r'^add/$',
        login_required(VideoCreateView.as_view()),
        name='video-add'
    ),
    url(r'^(?P<pk>[\d]+)/edit/$',
        VideoUpdateView.as_view(template_name_suffix='_edit_form'),
        name='video-edit'
    ),
    url(r'^archive/$',
        VideoListView.as_view(),
        name='video-list'
    ),
    url(r'^multi-delete/$',
        VideosDeleteView.as_view(),
        name='videos-delete'
    ),
    url(r'^video-move/$',
        VideoMoveView.as_view(),
        name='video-move'
    ),
    url(r'^delete/(?P<pk>\w+)/$',
        login_required(VideoDeleteView.as_view()),
        name='video-delete'
    ),
    url(r'^(?P<pk>\w+)/$',
        DetailView.as_view(model=Video),
        name='video-detail'
    ),
#    url(r'^$',
#        upload_view,
#        name='VideoView'
#    ),
)