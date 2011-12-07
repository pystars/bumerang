# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

from apps.advices.views import *

urlpatterns = patterns('',
    url(r'^$', show_advices, name='AdvicesIndexView'),
    url(r'^(?P<url>[-//\w]+)$', show_advices_from_url, name='AdvicesUrlView'),
)