# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from bumerang.apps.bumerang_site.views import HomeView

urlpatterns = patterns(
    '',
    url(r'^$', HomeView.as_view(), name='home'),
)
