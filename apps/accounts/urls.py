# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

from apps.accounts.views import *

urlpatterns = patterns('',
    url(r'^registration/$', RegistrationFormView.as_view(), name='registration_form'),
)