# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from bumerang.apps.events.models import Event
from bumerang.apps.events.views import (
    EventListView, ParticipantCreateView, EventScoreCardView,
    EventEditInfoView, EventCreateView, EventEditLogoView,
    ParticipantUpdateView, EventNominationsUpdateView,
    EventGeneralRuleUpdateView, EventNewsUpdateView, ParticipantListView,
    EventJurorsUpdateView, EventPressListView, EventFilmsListView,
    ParticipantReviewView, EventContactsUpdateView, EventDetailView,
    ParticipantVideoRatingUpdate, EventNewsPostUpdateView,
    EventConditionsDetailView, SetWinnersView, EventWinnersListView,
    EventPublishWinners, ParticipantListCSVView, ParticipantConfirmView,
    ParticipantPrintView)


urlpatterns = patterns('',
    url(r'^$',
        EventListView.as_view(),
        name='event-list'
    ),

    url(r'^festivals/$',
        EventListView.as_view(),
        {'type': Event.FESTIVAL},
        name='festival-list'
    ),

    url(r'^contests/$',
        EventListView.as_view(),
        {'type': Event.CONTEST},
        'contest-list'
    ),

    url(r'^send-request/$',
        login_required(EventCreateView.as_view()),
        name='event-send-request',
    ),

    url(r'^event(?P<pk>[\d]+)/$',
        EventDetailView.as_view(),
        name='event-detail'
    ),

    url(r'^event(?P<pk>[\d]+)/scorecard\.xls$',
        login_required(EventScoreCardView.as_view()),
        name='event-scorecard'
    ),

    url(r'^event(?P<event_pk>[\d]+)/press/$',
        EventPressListView.as_view(),
        name='event-press'
    ),

    url(r'^event(?P<event_pk>[\d]+)/films/$',
        EventFilmsListView.as_view(),
        name='event-films'
    ),

    url(r'^event(?P<event_pk>[\d]+)/winners/$',
        EventWinnersListView.as_view(),
        name='event-winners-list'
    ),

    url(r'^event(?P<event_pk>[\d]+)/films/(?P<nomination_pk>[\d]+)$',
        EventFilmsListView.as_view(),
        name='event-films-by-id'
    ),

    url(r'^event(?P<pk>[\d]+)/request-conditions/$',
        EventConditionsDetailView.as_view(),
        name='event-request-conditions'
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

    url(r'^event(?P<event_id>[\d]+)/edit-newspost(?P<pk>[\d]+)/$',
        login_required(EventNewsPostUpdateView.as_view()),
        name='event-edit-news-post'
    ),

    url(r'^event(?P<pk>[\d]+)/edit-contacts/$',
        login_required(EventContactsUpdateView.as_view()),
        name='event-edit-contacts'
    ),

    url(r'^event(?P<event_pk>[\d]+)/edit-requests/$',
        login_required(ParticipantListView.as_view()),
        name='participant-list'
    ),

    url(r'^event(?P<event_pk>[\d]+)/request/$',
        login_required(ParticipantCreateView.as_view()),
        name='event-request-form'
    ),

    url(r'^participant(?P<pk>[\d]+)/confirm/$',
        login_required(ParticipantConfirmView.as_view()),
        name='participant-confirm'
    ),

    url(r'^participant(?P<pk>[\d]+)/edit/$',
        login_required(ParticipantUpdateView.as_view()),
        name='participant-edit'
    ),
    url(r'^participant(?P<pk>[\d]+)/print/$',
        ParticipantPrintView.as_view(),
        # login_required(ParticipantPrintView.as_view()),
        name='participant-print'
    ),

    url(r'^participant(?P<pk>[\d]+)/review/$',
        login_required(ParticipantReviewView.as_view()),
        name='participant-review'
    ),

    url(r'^participant-video(?P<pk>[\d]+)/(?P<rate>[\d]+)/$',
        ParticipantVideoRatingUpdate.as_view(),
        name='participant-video'
    ),

    url(r'^nomination(?P<nomination>[\d]+)/(?P<participant_video>[\d]+)/$',
        login_required(SetWinnersView.as_view()),
        name='nomination-set-winner'
    ),

    url(r'^event(?P<pk>[\d]+)/publish-winners/$',
        login_required(EventPublishWinners.as_view()),
        name='event-publish-winners'
    ),

    url(r'^event(?P<event_pk>[\d]+)/participant_video_list\.xls$',
        login_required(ParticipantListCSVView.as_view()),
        name='participant-video-list-csv'
    ),
)
