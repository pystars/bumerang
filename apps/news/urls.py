# -*- coding: utf-8 -*-

from django.views.generic import DetailView, ListView
from django.conf.urls.defaults import patterns, url

from apps.news.models import NewsItem
from apps.news.views import *

urlpatterns = patterns('',
    url(r'^$', NewsRootView.as_view(
        template_name = "news.html"
    ), name='NewsIndexView'),
    url(r'^(?P<slug>[-\w]+)/$', CategoryView.as_view(), name='CategoryView'),
    url(r'^(?P<category_slug>[-\w]+)/(?P<news_slug>[-\w]+)/$', SingleNewsItemView.as_view(), name='SingleNewsItemView'),
)