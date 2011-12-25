# -*- coding: utf-8 -*-
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.dispatch.dispatcher import receiver
from django.views.generic import CreateView, DetailView
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView

from apps.accounts.forms import RegistrationForm, PasswordRecoveryForm
from apps.accounts.models import Profile


class RegistrationFormView(CreateView):
    form_class = RegistrationForm
    template_name = "accounts/registration.html"

    def get_success_url(self):
        return HttpResponseRedirect('/')


class ProfileView(DetailView):
    model = Profile


class PasswordRecoveryView(FormView):
    form_class = PasswordRecoveryForm
    template_name = "accounts/password_recovery.html"

    def form_valid(self, form):
        try:
            profile = Profile.objects.get(e_mail=form.fields['email'])
        except ObjectDoesNotExist:
            form.fields['email'].error_messages['invalid'] = u'Пользователь с таким адресом не существует'
            self.form_invalid(form)

        return HttpResponseRedirect(self.get_success_url())