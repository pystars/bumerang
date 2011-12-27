# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from apps.accounts.views import *


urlpatterns = patterns('',
    url(r'^$', UsersListView.as_view(), name="users-list"),
    url(r'^registration/$', RegistrationFormView.as_view(), name='registration'),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^recover/$', PasswordRecoveryView.as_view(), name='password-recover'),
    url(r'^logout/$', 'django.contrib.auth.views.logout'),
    url(r'^profile/$', login_required(ProfileView.as_view()), name='profile-self'),
    url(r'^edit$', login_required(ProfileInfoEditView.as_view(template_name_suffix='_edit_info')), name='profile-edit'),
    url(r'^edit-avatar$', login_required(ProfileAvatarEditView.as_view(template_name_suffix='_edit_avatar')), name='profile-edit-avatar'),
    url(r'^edit-resume$', login_required(ProfileResumeEditView.as_view(template_name_suffix='_edit_resume')), name='profile-edit-resume'),

    url(r'^(?P<pk>[\d]+)/video/$', ProfileVideoView.as_view(template_name_suffix='_video'), name='profile_video'),
    url(r'^(?P<pk>[\d]+)/$', ProfileView.as_view(), name='profile-detail'),
)