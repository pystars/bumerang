# -*- coding: utf-8 -*-

from django.views.generic import TemplateView
from django.conf.urls.defaults import patterns, url

from apps.video.views import *

urlpatterns = patterns('',
    url(r'^$', upload_view, name='VideoView'),
)