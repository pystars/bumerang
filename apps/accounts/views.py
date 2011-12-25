# -*- coding: utf-8 -*-
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