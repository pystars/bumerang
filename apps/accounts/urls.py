# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from apps.accounts.views import RegistrationFormView, ProfileView, ProfileVideoView


urlpatterns = patterns('',
    url(r'^registration/$', RegistrationFormView.as_view(), name='registration_form'),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^recover/$', PasswordRecoveryView.as_view(), name='password_recover'),
    url(r'^user/(?P<pk>[\d]+)/$', ProfileView.as_view(), name='profile_view'),
    url(r'^logout/$', 'django.contrib.auth.views.logout'),
    url(r'^profile/$', ProfileView.as_view()),
    url(r'^(?P<pk>[\d]+)/video/$', ProfileView.as_view(template_name_suffix='_video'), name='profile_video'),
    url(r'^(?P<pk>[\d]+)/$', ProfileView.as_view(), name='profile_view'),

)