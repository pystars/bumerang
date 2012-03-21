# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from bumerang.apps.advices.views import AdvicesListView, AdviceDetailView


urlpatterns = patterns('',
    url(r'^$',
        AdvicesListView.as_view(),
        name='advice-list'
    ),
    url(r'^(?P<slug>[-//\w]+)/$',
        AdviceDetailView.as_view(),
        name='advice-detail'
    ),
)