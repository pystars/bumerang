# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from bumerang.apps.utils.views import (XMLDetailView, ObjectsDeleteView,
    AjaxRatingView)
from bumerang.apps.video.albums.views import VideoAlbumDetailView
from bumerang.apps.video.views import VideoListAjaxView, VideoGetS3UploadURLView
from .models import Video
from albums.models import VideoAlbum
from .views import (VideoListView, VideoCreateView, VideoDetailView,
    VideoUpdateView, VideoMoveView, endpoint)
from albums.views import (VideoAlbumCreateView, VideoSetCoverView,
    VideoAlbumUpdateView)


urlpatterns = patterns(
    '',
    url(r'^$',
        VideoListView.as_view(),
        name='video-list'),

    url(r'^endpoint$',
        endpoint,
        name='video-endpoint'),

    url(r'^~(?P<category>[\w\-]+)/$',
        VideoListView.as_view(),
        name='video-list-category'),
    # AJAX video list
    url(r'^ajax/(?P<pk>[\d]+)/$',
        VideoListAjaxView.as_view(),
        name='video-list-ajax'),

    url(r'^album/add/$',
        login_required(VideoAlbumCreateView.as_view()),
        name='video-album-add'),

    url(r'^album(?P<video_album_id>[\d]+)/add/$',
        login_required(VideoCreateView.as_view()),
        name='album-video-add'),

    url(r'^album(?P<pk>[\d]+)/$',
        VideoAlbumDetailView.as_view(),
        name='video-album-detail'),

    url(r'^album(?P<pk>[\d]+)/edit/$',
        login_required(VideoAlbumUpdateView.as_view()),
        name='video-album-edit'),

    url(r'^album(?P<pk>[\d]+)/set-cover/$',
        login_required(VideoSetCoverView.as_view()),
        name='video-album-cover'),

    url(r'^add/$',
        login_required(VideoCreateView.as_view()),
        name='video-add'),

    url(r'^(?P<pk>[\d]+)/edit/$',
        login_required(VideoUpdateView.as_view()),
        name='video-edit'),

    url(r'^(?P<pk>[\d]+)/get-s3-upload-url/$',
        login_required(VideoGetS3UploadURLView.as_view()),
        name='video-get-s3-upload-url'),

    url(r'^videos-delete/$',
        login_required(ObjectsDeleteView.as_view(model=Video)),
        name='videos-delete'),

    url(r'^albums-delete/$',
        login_required(ObjectsDeleteView.as_view(model=VideoAlbum)),
        name='videoalbums-delete'),

    url(r'^video-move/$',
        login_required(VideoMoveView.as_view()),
        name='video-move'),

    url(r'^(?P<pk>\w+).xml$',
        XMLDetailView.as_view(
            model=Video, template_name_suffix='_xml'),
        name='video-xml'),

    # Ratings
    url(r'^rate/(?P<object_id>\d+)/(?P<score>\d+)/$',
        login_required(AjaxRatingView()), {
            'app_label': 'video',
            'model': 'video',
            'field_name': 'rating',
        },
        name='video-rate'),

    url(r'^(?P<pk>\w+)/$',
        VideoDetailView.as_view(),
        name='video-detail'),
)
