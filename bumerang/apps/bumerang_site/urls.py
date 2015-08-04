# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from bumerang.apps.bumerang_site.views import BumerangIndexView

urlpatterns = patterns(
    '',
    url(r'^$', BumerangIndexView.as_view(), name='home'),
)
