# -*- coding: utf-8 -*-

from django.views.generic import DetailView, ListView
from django.conf.urls.defaults import patterns, url

from apps.news.models import NewsItem

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(
        model = NewsItem,
        template_name = "news.html"
    ), name='NewsIndexView'),
    url(r'^(?P<slug>[-\w]+)/$', DetailView.as_view(
        model=NewsItem,
        template_name="single_news.html"
    ), name='SingleNewsView'),
)