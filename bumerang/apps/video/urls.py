# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView

from bumerang.apps.utils.views import XMLDetailView, ObjectsDeleteView
from models import Video
from albums.models import VideoAlbum
from views import (VideoListView, VideoCreateView, VideoDetailView,
    VideoUpdateView, VideoMoveView)
from albums.views import (VideoAlbumCreateView, VideoSetCoverView,
    VideoAlbumUpdateView)


urlpatterns = patterns('',
    url(r'^album/add/$',
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
    url(r'^album(?P<pk>[\d]+)/set-cover/$',
        login_required(VideoSetCoverView.as_view()),
        name='video-album-cover'
    ),
    url(r'^add/$',
        login_required(VideoCreateView.as_view()),
        name='video-add'
    ),
    url(r'^(?P<pk>[\d]+)/edit/$',
        login_required(VideoUpdateView.as_view()),
        name='video-edit'
    ),
    url(r'^$',
        VideoListView.as_view(),
        name='video-list'
    ),
    url(r'^videos-delete/$',
        login_required(ObjectsDeleteView.as_view(model=Video)),
        name='videos-delete'
    ),
    url(r'^albums-delete/$',
        login_required(ObjectsDeleteView.as_view(model=VideoAlbum)),
        name='videoalbums-delete'
    ),
    url(r'^video-move/$',
        login_required(VideoMoveView.as_view()),
        name='video-move'
    ),
#    url(r'^delete/(?P<pk>\w+)/$',
#        login_required(VideoDeleteView.as_view()),
#        name='video-delete'
#    ),
    url(r'^(?P<pk>\w+)/$',
        VideoDetailView.as_view(),
        name='video-detail'
    ),
    url(r'^(?P<pk>\w+).xml$',
        XMLDetailView.as_view(
            model=Video, template_name_suffix='_xml'),
        name='video-xml'
    ),
)
