# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

from apps.advices.views import *

urlpatterns = patterns('',
    url(r'^$', AdvicesIndexView.as_view(), name='AdvicesIndexView'),
    url(r'^(?P<url>[-//\w]+)/$', SingleAdviceView.as_view(), name='AdvicesUrlView'),
)