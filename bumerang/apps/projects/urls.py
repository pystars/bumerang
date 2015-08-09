# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import ProjectDetailView, ProjectListView


urlpatterns = patterns(
    '',
    url(r'^$',
        ProjectListView.as_view(),
        name='project-list'
    ),
    url(r'^(?P<pk>\d+)/$',
        ProjectDetailView.as_view(),
        name='project-detail'
    ),
)
