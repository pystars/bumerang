# -*- coding: utf-8 -*-
from __future__ import division
import json
try:
    from cStringIO import StringIO
except ImportError:
    import StringIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.views.generic import CreateView, DetailView
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm

from apps.accounts.forms import *
from apps.accounts.models import Profile


class RegistrationFormView(CreateView):
    form_class = RegistrationForm
    template_name = "accounts/registration.html"

    def get_success_url(self):
        return reverse('BumerangIndexView')

    def form_valid(self, form):
        self.object = form.save()
        messages.add_message(self.request, messages.SUCCESS, u'Регистрация прошла успешно. Теперь вы можете залогиниться.')
        return super(RegistrationFormView, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, u'Ошибка при регистрации')
        return self.render_to_response(self.get_context_data(form=form))

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


class ProfileUpdateView(UpdateView):
    model = Profile

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return self.request.path


class ProfileAvatarEditView(UpdateView):
    model = Profile
    form_class = ProfileAvatarEditForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse('profile-edit-avatar')

    def form_valid(self, form):
        try:
            coords = json.loads(form.cleaned_data['avatar_coords'])
        except ValueError:
            coords = {
                'x': 0,
                'y': 0,
                'x2': 150,
                'y2': 150,
            }
        """
        Эта константа зависит от шаблона страницы
        и означает максимальную ширину изображения
        так как будучи большим, оно может выйти за
        рамки шаблона. Фактически, константа должна
        быть тождественна свойству max-width картинки
        с Crop'ом. Если исходное изображение шире этой
        константы, оно будет ужато для обеспечения совместимости
        координат, переданных Crop'ом
        """
        MAX_WIDTH = 710

        '''
        Загружен ли уже аватар и мы только должны
        его обрезать?
        '''
        img = Image.open(self.request.FILES.get('avatar', self.object.avatar))
        # Если изображение слишком широкое, ужимаем
        if img.size[0] > MAX_WIDTH:
            aspect = img.size[0] / img.size[1]
            new_height = int(round(img.size[1] * aspect))
            # Вот с этим изображением мы и будем работать
            img = img.resize((MAX_WIDTH, new_height), Image.ANTIALIAS)
        # Иначе просто обрезаем
        cropped_image = img.crop((coords['x'],
                                  coords['y'],
                                  coords['x2'],
                                  coords['y2']))
        cropped_image.thumbnail((180, 180), Image.ANTIALIAS)


        temp_handle = StringIO()
        cropped_image.save(temp_handle, 'jpeg')
        temp_handle.seek(0)

        suf = SimpleUploadedFile('min.jpg',
            temp_handle.read(), content_type='image/jpg')

        self.object.min_avatar.save('min.jpg', suf, save=False)
        form.save()
        messages.add_message(self.request, messages.SUCCESS, u'Фотография профиля успешно обновлена')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, u'Ошибка при обновлении фотографии профиля')
        return self.render_to_response(self.get_context_data(form=form))


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
                pwd_form.save()
                messages.add_message(self.request, messages.SUCCESS, u'Пароль успешно изменен')
                return self.render_to_response(self.get_context_data())
            else:
                messages.add_message(self.request, messages.ERROR, u'Ошибка при изменении пароля')
                return self.render_to_response(self.get_context_data(pwd_form=pwd_form))

        if 'email' in request.POST:
            email_form = ProfileEmailEditForm(request.POST)
            if email_form.is_valid():
                self.request.user = email_form.save()
                messages.add_message(self.request, messages.SUCCESS, u'Почтовый адрес успешно изменен')
                return self.render_to_response(self.get_context_data())
            else:
                messages.add_message(self.request, messages.ERROR, u'Ошибка при изменении почтового адреса')
                return self.render_to_response(self.get_context_data(email_form=email_form))