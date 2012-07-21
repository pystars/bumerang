# -*- coding: utf-8 -*-
#from django.conf.urls.defaults import patterns, url
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from bumerang.apps.festivals.forms import FestivalNominationForm, \
    FestivalGeneralRuleForm
from bumerang.apps.festivals.models import FestivalNomination, \
    Festival, FestivalGeneralRule
from bumerang.apps.festivals.views import FestivalListView, \
    FestivalSendRequest, FestivalDetailView, FestivalEditInfoView, \
    FestivalEditLogoView, FestivalFormsetGenericView, FestivalRequestFormView

urlpatterns = patterns('',
    url(r'^$',
        FestivalListView.as_view(),
        name='festival-list'
    ),

    url(r'^send-request/$',
        login_required(FestivalSendRequest.as_view()),
        name='festival-send-request',
    ),

    url(r'^fest(?P<pk>[\d]+)/$',
        FestivalDetailView.as_view(),
        name='festival-detail'
    ),

    url(r'^fest(?P<pk>[\d]+)/edit/$',
        login_required(FestivalEditInfoView.as_view()),
        name='festival-edit-info'
    ),

    url(r'^fest(?P<pk>[\d]+)/edit-logo/$',
        login_required(FestivalEditLogoView.as_view()),
        name='festival-edit-logo'
    ),

#    url(r'^fest(?P<pk>[\d]+)/edit-nominations/$',
#        login_required(FestivalEditNominationsView.as_view()),
#        name='festival-edit-nominations'
#    )

    url(r'^fest(?P<pk>[\d]+)/edit-nominations/$',
        login_required(FestivalFormsetGenericView.as_view(
            model=Festival,
            formset_model=FestivalNomination,
            form_class=FestivalNominationForm,
            template_name="festivals/festival_edit_formset.html",
            add_item_text=u'Добавить номинацию'
        )),
        name='festival-edit-nominations'
    ),

    url(r'^fest(?P<pk>[\d]+)/edit-rules/$',
        login_required(FestivalFormsetGenericView.as_view(
            model=Festival,
            formset_model=FestivalGeneralRule,
            form_class=FestivalGeneralRuleForm,
            template_name="festivals/festival_edit_formset.html",
            add_item_text=u'Добавить положение'
        )),
        name='festival-edit-rules'
    ),

    url(r'^fest(?P<pk>[\d]+)/festival-request/$',
        login_required(FestivalRequestFormView.as_view()),
        name='festival-request-form'
    ),

)
