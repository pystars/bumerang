# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from apps.accounts.views import *


urlpatterns = patterns('',
    url(r'^registration/$', RegistrationFormView.as_view(), name='registration_form'),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^user/(?P<pk>[\d]+)/$', ProfileView.as_view(), name='profile_view'),
)