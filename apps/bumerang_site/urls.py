# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

from apps.bumerang_site.views import BumerangIndexView

urlpatterns = patterns('',
    url(r'^$', BumerangIndexView.as_view(), name='BumerangIndexView'),
)