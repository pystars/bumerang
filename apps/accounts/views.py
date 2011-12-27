# -*- coding: utf-8 -*-
import random

from django.contrib.auth.models import get_hexdigest
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.views.generic import CreateView, DetailView
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django_extensions.utils.uuid import uuid4

from apps.accounts.forms import *
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
        receiver_email = form.data['email']
        new_password = uuid4().get_hex()[:8]

        salt = get_hexdigest('sha1', str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest('sha1', salt, new_password)
        new_password_hash = '%s$%s$%s' % ('sha1', salt, hsh)

        profile = Profile.objects.get(e_mail=receiver_email)
        profile.password = new_password_hash
        profile.save()
        #TODO: Сделать отправку почты через шаблоны и класс работы с почтой
        send_mail(
            u'Восстановление пароля от сервиса БумерангПРО',
            u'Ваш новый пароль: %s' % new_password,
            u'alexilorenz@gmail.com',
            [receiver_email],
        )

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


class UsersListView(ListView):
    model = Profile
    paginate_by = 25


class ProfileInfoEditView(UpdateView):
    model = Profile
    form_class = ProfileInfoEditForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse("profile-edit")


class ProfileAvatarEditView(UpdateView):
    model = Profile
    form_class = ProfileAvatarEditForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse('profile-edit-avatar')


class ProfileResumeEditView(UpdateView):
    model = Profile
    form_class = ProfileResumeEditForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse('profile-edit-resume')