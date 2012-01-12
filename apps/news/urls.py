# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from apps.news.views import *

urlpatterns = patterns('',
    url(r'^$',
        NewsListView.as_view(),
        name='news-list'
    ),
    url(r'^(?P<category>[-\w]+)/$',
        NewsListView.as_view(),
        name='news-list-category'
    ),
    url(r'^(?P<category>[-\w]+)/(?P<slug>[-\w]+)/$',
        NewsItemDetailView.as_view(),
        name='news-detail'
    ),
)