# -*- coding: utf-8 -*-
from django.contrib.auth.signals import user_logged_in
from django.dispatch.dispatcher import receiver
from django.views.generic import CreateView, DetailView
from django.http import HttpResponseRedirect

from apps.accounts.forms import RegistrationForm
from apps.accounts.models import Profile


class RegistrationFormView(CreateView):
    form_class = RegistrationForm
    template_name = "accounts/registration.html"

    def get_success_url(self):
        return HttpResponseRedirect('/')


class ProfileView(DetailView):
    model = Profile
