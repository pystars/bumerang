# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from apps.accounts.views import *


urlpatterns = patterns('',
    url(r'^$', UsersListView.as_view(), name="users-list"),
    url(r'^registration/$', RegistrationFormView.as_view(), name='registration_form'),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^recover/$', PasswordRecoveryView.as_view(), name='password_recover'),
    url(r'^logout/$', 'django.contrib.auth.views.logout'),
    url(r'^profile/$', login_required(ProfileView.as_view()), name='profile-self'),
    url(r'^edit/info$', login_required(ProfileInfoEditView.as_view()), name='profile-edit'),

    url(r'^(?P<pk>[\d]+)/video/$', ProfileVideoView.as_view(template_name_suffix='_video'), name='profile_video'),
    url(r'^(?P<pk>[\d]+)/$', ProfileView.as_view(), name='profile-detail'),

)