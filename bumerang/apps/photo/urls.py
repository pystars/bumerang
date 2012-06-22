# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from bumerang.apps.photo.albums.views import PhotoAlbumDetailView
from bumerang.apps.photo.views import increase_views_count, PhotoAlbumListView

from bumerang.apps.utils.views import ObjectsDeleteView
from models import Photo
from albums.models import PhotoAlbum
from views import (PhotoListView, PhotoCreateView, PhotoDetailView,
    PhotoUpdateView, PhotoMoveView)
from albums.views import (PhotoAlbumCreateView, PhotoSetCoverView,
    PhotoAlbumUpdateView)


urlpatterns = patterns('',
    url(r'^album/add/$',
        login_required(PhotoAlbumCreateView.as_view()),
        name='photo-album-add'
    ),
    url(r'^album(?P<photo_album_id>[\d]+)/add/$',
        login_required(PhotoCreateView.as_view()),
        name='album-photo-add'
    ),
    url(r'^album(?P<pk>[\d]+)/$',
        PhotoAlbumDetailView.as_view(),
        name='photo-album-detail'
    ),
    url(r'^album(?P<pk>[\d]+)/edit/$',
        login_required(PhotoAlbumUpdateView.as_view()),
        name='photo-album-edit'
    ),
    url(r'^album(?P<pk>[\d]+)/set-cover/$',
        login_required(PhotoSetCoverView.as_view()),
        name='photo-album-cover'
    ),
    url(r'^add/$',
        login_required(PhotoCreateView.as_view()),
        name='photo-add'
    ),
    url(r'^(?P<pk>[\d]+)/edit/$',
        login_required(PhotoUpdateView.as_view()),
        name='photo-edit'
    ),
    url(r'^$',
        PhotoAlbumListView.as_view(),
        name='photo-list'
    ),
    url(r'^photos-delete/$',
        login_required(ObjectsDeleteView.as_view(model=Photo)),
        name='photos-delete'
    ),
    url(r'^albums-delete/$',
        login_required(ObjectsDeleteView.as_view(model=PhotoAlbum)),
        name='photoalbums-delete'
    ),
    url(r'^photo-move/$',
        login_required(PhotoMoveView.as_view()),
        name='photo-move'
    ),
    url(r'^(?P<pk>\w+)/$',
        PhotoDetailView.as_view(),
        name='photo-detail'
    ),

    url(r'^(?P<pk>[\d]+)/update-count/$',
        increase_views_count,
        name='photo-update-count'
    ),

    url(r'^~(?P<category>[\w\-]+)/$',
        PhotoAlbumListView.as_view(),
        name='photo-list-category'
    ),
)
