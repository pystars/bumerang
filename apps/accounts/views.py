# -*- coding: utf-8 -*-
from django.views.generic import CreateView

from apps.accounts.forms import RegistrationForm


class RegistrationFormView(CreateView):
    form_class = RegistrationForm
    template_name = "accounts/registration.html"
