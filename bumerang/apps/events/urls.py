# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from bumerang.apps.events.views import (EventListView, ParticipantCreateView,
    EventDetailView, EventEditInfoView, EventCreateView, EventEditLogoView,
    ParticipantUpdateView, EventNominationsUpdateView,
    EventGeneralRuleUpdateView, EventNewsUpdateView, ParticipantListView,
    EventJurorsUpdateView)


urlpatterns = patterns('',
    url(r'^$',
        EventListView.as_view(),
        name='event-list'
    ),

    url(r'^send-request/$',
        login_required(EventCreateView.as_view()),
        name='event-send-request',
    ),

    url(r'^event(?P<pk>[\d]+)/$',
        EventDetailView.as_view(),
        name='event-detail'
    ),

    url(r'^event(?P<pk>[\d]+)/edit/$',
        login_required(EventEditInfoView.as_view()),
        name='event-edit-info'
    ),

    url(r'^event(?P<pk>[\d]+)/edit-logo/$',
        login_required(EventEditLogoView.as_view()),
        name='event-edit-logo'
    ),

    url(r'^event(?P<pk>[\d]+)/edit-nominations/$',
        login_required(EventNominationsUpdateView.as_view()),
        name='event-edit-nominations'
    ),

    url(r'^event(?P<pk>[\d]+)/edit-rules/$',
        login_required(EventGeneralRuleUpdateView.as_view()),
        name='event-edit-rules'
    ),

    url(r'^event(?P<pk>[\d]+)/edit-jurors/$',
        login_required(EventJurorsUpdateView.as_view()),
        name='event-edit-jurors'
    ),

    url(r'^event(?P<pk>[\d]+)/edit-news/$',
        login_required(EventNewsUpdateView.as_view()),
        name='event-edit-news'
    ),

    url(r'^event(?P<event_pk>[\d]+)/edit-requests/$',
        login_required(ParticipantListView.as_view()),
        name='participant-list'
    ),

    url(r'^event(?P<event_pk>[\d]+)/request/$',
        login_required(ParticipantCreateView.as_view()),
        name='event-request-form'
    ),

    url(r'^participant(?P<pk>[\d]+)/edit/$',
        login_required(ParticipantUpdateView.as_view()),
        name='participant-edit'
    ),
)
