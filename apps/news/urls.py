# -*- coding: utf-8 -*-

from django.views.generic import DetailView, ListView
from django.conf.urls.defaults import patterns, url

from apps.news.models import NewsItem
from apps.news.views import NewsRootView

urlpatterns = patterns('',
    url(r'^$', NewsRootView.as_view(
        #model = NewsItem,
        template_name = "news.html"
    ), name='NewsIndexView'),
    url(r'^(?P<slug>[-\w]+)/$', DetailView.as_view(
        model=NewsItem,
        template_name="single_news.html"
    ), name='SingleNewsView'),
)