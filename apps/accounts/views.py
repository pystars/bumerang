# -*- coding: utf-8 -*-
import random

from django.contrib.auth.models import get_hexdigest
from django.core.mail import send_mail
from django.views.generic import CreateView, DetailView
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from django_extensions.utils.uuid import uuid4

from apps.accounts.forms import RegistrationForm, PasswordRecoveryForm
from apps.accounts.models import Profile


class RegistrationFormView(CreateView):
    form_class = RegistrationForm
    template_name = "accounts/registration.html"

    def get_success_url(self):
        return HttpResponseRedirect('/')


class PasswordRecoveryView(FormView):
    form_class = PasswordRecoveryForm
    template_name = "accounts/password_recovery.html"

    def form_valid(self, form):
        new_password = uuid4().get_hex()[:8]

        salt = get_hexdigest('sha1', str(random.random()), str(random.random()))[:5]
        hash = get_hexdigest('sha1', salt, new_password)

        send_mail()

        return HttpResponseRedirect(self.get_success_url())


class ProfileView(DetailView):
    model = Profile

    def get_object(self, queryset=None):
        if 'pk' not in self.kwargs:
            return self.request.user.profile
        return super(ProfileView, self).get_object(queryset=queryset)


class ProfileVideoView(DetailView):
    model = Profile

    def get_context_data(self, **kwargs):
        ctx = super(ProfileVideoView, self).get_context_data(**kwargs)
        ctx.update({'video_albums': self.object.videoalbum_set.all()})
        ctx.update({'videos': self.object.video_set.all()})
        return ctx
