# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.generic import CreateView
from django.http import HttpResponseRedirect

from apps.accounts.forms import RegistrationForm


class RegistrationFormView(CreateView):
    form_class = RegistrationForm
    template_name = "accounts/registration.html"

    def form_valid(self, form):
        print 'asd'

#    def post(self, request, *args, **kwargs):
#        form = RegistrationForm(request.POST)
#
#        if form.is_valid():
#            return HttpResponseRedirect('/')
#        else:
#            return render_to_response('accounts/registration.html',
#                { 'form': form },
#                context_instance=RequestContext(request)
#            )
