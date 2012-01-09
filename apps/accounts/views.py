# -*- coding: utf-8 -*-
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.views.generic import CreateView, DetailView
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.contrib import messages

from apps.accounts.forms import *
from apps.accounts.models import Profile


class RegistrationFormView(CreateView):
    form_class = RegistrationForm
    template_name = "accounts/registration.html"

    def get_success_url(self):
        return reverse('BumerangIndexView')


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
    #form_class = ProfileInfoEditForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_form_class(self):
        # Выбираем тип формы
        # в зависимости от типа профиля
        if self.request.user.profile.type == 1:
            return UserProfileInfoForm
        if self.request.user.profile.type == 2:
            return SchoolProfileInfoForm
        if self.request.user.profile.type == 3:
            return StudioProfileInfoForm

    def get_success_url(self):
        return reverse("profile-edit")

    def form_valid(self, form):
        self.object = form.save()
        messages.add_message(self.request, messages.SUCCESS, u'Профиль успешно обновлен')
        return super(ProfileInfoEditView, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, u'Ошибка при обновлении профиля')
        return self.render_to_response(self.get_context_data(form=form))


class ProfileFacultiesEditView(UpdateView):
    model = Profile
    form_class = SchoolProfileFacultiesForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse("profile-edit-faculties")


class ProfileTeachersEditView(UpdateView):
    model = Profile
    form_class = SchoolProfileTeachersForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse("profile-edit-teachers")


class ProfileServicesEditView(UpdateView):
    model = Profile
    form_class = StudioProfileServicesForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse("profile-edit-services")


class ProfileTeamEditView(UpdateView):
    model = Profile
    form_class = StudioProfileTeamForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse("profile-edit-team")


class ProfileAvatarEditView(UpdateView):
    model = Profile
    form_class = ProfileAvatarEditForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse('profile-edit-avatar')

    def form_valid(self, form):
        import json
        coords = json.loads(form.cleaned_data['coords'])
        messages.add_message(self.request, messages.ERROR, u'Фотография профиля успешно обновлена')
        return self.render_to_response(self.get_context_data(form=form))


class ProfileResumeEditView(UpdateView):
    model = Profile
    form_class = ProfileResumeEditForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse('profile-edit-resume')


class ProfileSettingsEditView(TemplateView):
    template_name = "accounts/profile_edit_settings.html"

    def get_context_data(self, **kwargs):
        ctx = super(ProfileSettingsEditView, self).get_context_data(**kwargs)
        ctx.update({
            'email_form': ProfileEmailEditForm(),
            'pwd_form': PasswordChangeForm(self.request.user),
        })
        ctx.update(kwargs)
        return ctx

    def get_object(self, queryset=None):
        return self.request.user.profile

    def post(self, request):
        if 'old_password' in request.POST:
            pwd_form = PasswordChangeForm(self.request.user, request.POST)
            if pwd_form.is_valid():
                messages.add_message(self.request, messages.SUCCESS, u'Пароль успешно изменен')
                return self.render_to_response(self.get_context_data())
            else:
                messages.add_message(self.request, messages.ERROR, u'Ошибка при изменении пароля')
                return self.render_to_response(self.get_context_data(pwd_form=pwd_form))

        if 'email' in request.POST:
            email_form = ProfileEmailEditForm(request.POST)
            if email_form.is_valid():
                messages.add_message(self.request, messages.SUCCESS, u'Почтовый адрес успешно изменен')
                return self.render_to_response(self.get_context_data())
            else:
                messages.add_message(self.request, messages.ERROR, u'Ошибка при изменении почтового адреса')
                return self.render_to_response(self.get_context_data(email_form=email_form))