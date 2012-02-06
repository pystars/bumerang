# -*- coding: utf-8 -*-
from __future__ import division
import json
from PIL import Image
from datetime import datetime, timedelta

try:
    from cStringIO import StringIO
except ImportError:
    import StringIO

from django.contrib.sites.models import Site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.views.generic import CreateView, DetailView, TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.forms.models import inlineformset_factory

from apps.accounts.forms import *
from apps.accounts.models import Profile, TeachersRelationship
from apps.utils.email import send_activation_success
from apps.utils.tasks import send_new_password_task, send_activation_link_task

def notify_success(request, message):
    '''
    Выводит уведомление об успешном сохранении информации профиля
    '''
    messages.add_message(request, messages.SUCCESS, message)
    return

def notify_error(request, message):
    '''
    Выводит уведомление об ошибке при сохранении информации профиля
    '''
    messages.add_message(request, messages.ERROR, message)
    return


class RegistrationFormView(CreateView):
    form_class = RegistrationForm
    template_name = "accounts/registration.html"

    def get_success_url(self):
        return reverse('BumerangIndexView')

    def form_valid(self, form):
        self.object = form.save()

        activation_code = get_hexdigest('sha1',
                             str(random.random()),
                             str(random.random()))[:32]

        self.object.is_active = False
        self.object.activation_code = activation_code

        current_site = Site.objects.get_current()
        url = reverse('activate-account', args=[activation_code])

        full_activation_url = 'http://{0}{1}'.format(current_site, url)
        self.object.activation_code_expire = datetime.now() + timedelta(days=1)

        send_activation_link_task(full_activation_url,
                                  form.cleaned_data['email'])

        self.object.save()

        notify_success(
            self.request,
            message=u'''
            Регистрация прошла успешно. Вам была отправлена ссылка
            для активации аккаунта.
            Проверьте почту и активируйте ваш аккаунт.
            '''
        )

        return super(RegistrationFormView, self).form_valid(form)

    def form_invalid(self, form):
        notify_error(
            self.request,
            message=u'''
            При регистрации произошла ошибка.
            '''
        )

        return self.render_to_response(self.get_context_data(form=form))


class AccountActivationView(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            user = Profile.objects.get(activation_code=kwargs['code'])

            if user.activation_code_expire < datetime.now():
                user.delete()

                notify_error(
                    self.request,
                    message=u'''
                    С момента регистрации прошло больше суток и активационная
                    ссылка устарела.
                    Пройдите процедуру <a href="%s">регистрации</a> заново.
                    ''' % reverse('registration')
                )

                return HttpResponseRedirect(reverse('BumerangIndexView'))

            user.is_active = True
            user.activation_code = ''
            user.save()
            notify_success(
                self.request,
                message=u'''
                Ваш аккаунт успешно активирован.
                Теперь вы можете <a href="%s">войти</a> в систему.
                ''' % reverse('login')
            )

            send_activation_success(user.email)

            return HttpResponseRedirect(reverse('BumerangIndexView'))

        except ObjectDoesNotExist:
            notify_error(
                self.request,
                message=u'''
                При активации аккаунта произошла ошибка.
                Возможно, аккаунт уже был активирован ранее,
                либо срок действия ссылки истёк.
                '''
            )

            return HttpResponseRedirect(reverse('BumerangIndexView'))


class PasswordRecoveryView(FormView):
    form_class = PasswordRecoveryForm
    template_name = "accounts/password_recovery.html"

    def get_success_url(self):
        return '/'

    def form_valid(self, form):
        receiver_email = form.data['email']
        new_password = uuid4().get_hex()[:8]
        salt = get_hexdigest(
            'sha1', str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest('sha1', salt, new_password)
        new_password_hash = '%s$%s$%s' % ('sha1', salt, hsh)

        profile = Profile.objects.get(email=receiver_email)
        profile.password = new_password_hash
        profile.save()

        send_new_password_task.delay(new_password, receiver_email)
        notify_success(
            self.request,
            message=u'''
                Ваш новый пароль был отправлен на указанный вами e-mail.
                После авторизации вы сможете его сменить в разделе
                редактирования профиля.
                '''
        )

        return HttpResponseRedirect(self.get_success_url())


class ProfileView(DetailView):
    model = Profile

    def get_object(self, queryset=None):
        if 'pk' not in self.kwargs:
            return self.request.user.profile
        return super(ProfileView, self).get_object(queryset=queryset)

    def get(self, request, **kwargs):
        response = super(ProfileView, self).get(request, **kwargs)

        try:
            user_id = request.user.profile.id
        except AttributeError:
            user_id = None

        if self.get_object().id == user_id:
            return response
        else:
            Profile.objects.filter(pk=self.get_object().id).update(
                views_count=self.get_object().views_count + 1)

        return response


class ProfileVideoView(DetailView):
    model = Profile

    def get_context_data(self, **kwargs):
        ctx = super(ProfileVideoView, self).get_context_data(**kwargs)
        ctx.update({'video_albums': self.object.videoalbum_set.all()})
        ctx.update({'videos': self.object.video_set.all()})
        return ctx


class UsersListView(ListView):
    queryset = Profile.objects.filter(
        is_active=True,
        title__isnull=False
    ).order_by('-id')
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
        notify_success(
            self.request,
            message=u'''
                Данные профиля успешно обновлены.
                '''
        )

        return super(ProfileInfoEditView, self).form_valid(form)

    def form_invalid(self, form):
        notify_error(
            self.request,
            message=u'''
                При обновлении данных профиля произошла ошибка.
                '''
        )

        return self.render_to_response(self.get_context_data(form=form))


class ProfileUpdateView(UpdateView):
    model = Profile

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        notify_success(
            self.request,
            message=u'''
                Данные профиля успешно обновлены.
                '''
        )

        return super(ProfileUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        notify_error(
            self.request,
            message=u'''
                При обновлении данных профиля произошла ошибка.
                '''
        )

        return super(ProfileUpdateView, self).form_invalid(form)

class FormsetUpdateView(UpdateView):
    template_name = "accounts/profile_formset.html"
    fk_name = None
    model = None
    form = None

    def __init__(self, **kwargs):
        for kw, arg in kwargs.iteritems():
            setattr(self, kw, arg)

        self.FormSet = inlineformset_factory(
            parent_model=Profile,
            model=self.model,
            form=self.form,
            fk_name=self.fk_name,
            extra=1)

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = kwargs
        context['object'] = self.get_object()
        context_object_name = self.get_context_object_name(self.get_object())
        if context_object_name:
            context[context_object_name] = self.get_object()
        if not 'formset' in context:
            context['formset'] = self.FormSet(instance=self.get_object())
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(FormsetUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        formset = self.FormSet(request.POST, instance=self.get_object())

        if formset.is_valid():
            formset.save()
            notify_success(
                self.request,
                message=u'''
                Данные профиля успешно обновлены.
                '''
            )

            return HttpResponseRedirect(self.get_success_url())
        else:
            self.object = self.get_object()
            notify_error(
                self.request,
                message=u'''
                При обновлении данных профиля произошла ошибка.
                '''
            )

            return self.render_to_response(self.get_context_data(formset=formset))


class TeachersEditView(UpdateView):
    form_class = TeacherForm
#    model = Profile

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_form(self, form_class):
        form = super(TeachersEditView, self).get_form(form_class)
        form.fields['teachers'].queryset = Profile.objects.exclude(id=self.get_object().id)
        return form

    def form_valid(self, form):
#        form.save()
        for account in form.cleaned_data['teachers']:
            rel = TeachersRelationship(from_profile=self.get_object(),
                                       to_profile=account,
                                       status=1)
            rel.save()
        return HttpResponseRedirect(self.get_success_url())

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

        notify_success(
            self.request,
            message=u'''
            Фотография профиля успешно обновлена.
            '''
        )

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        notify_error(
            self.request,
            message=u'''
            Произошла ошибка при обновлении фотографии профиля.
            Возможно, файл, который вы загрузили, поврежден
            или не является изображением.
            '''
        )

        return self.render_to_response(self.get_context_data(form=form))


class ProfileSettingsEditView(UpdateView):
    model = User
    email_form_class = ProfileEmailEditForm
    pwd_form_class = PasswordChangeForm
    template_name = "accounts/profile_edit_settings.html"

    def get_context_data(self, **kwargs):
        ctx = super(ProfileSettingsEditView, self).get_context_data(**kwargs)
        ctx.update({
            'email_form': self.email_form_class(),
            'pwd_form': self.pwd_form_class(self.get_object()),
        })
        ctx.update(kwargs)
        return ctx

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_class(self):
        if self.password_changing():
            return self.pwd_form_class
        return self.email_form_class

    def password_changing(self):
        if 'old_password' in self.request.POST:
            return True

    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()
        if issubclass(form_class, self.pwd_form_class):
            kwargs['user'] = kwargs.pop('instance')
        return form_class(**kwargs)

    def form_valid(self, form):
        message = u'Почтовый адрес успешно изменен.'
        if self.password_changing():
            message = u'Пароль успешно изменен.'

        notify_success(self.request, message=message)

        self.object = form.save()
        return self.render_to_response(self.get_context_data())

    def form_invalid(self, form):
        message = u'Ошибка при изменении почтового адреса.'
        form_name = 'email_form'
        if self.password_changing():
            message = u'Ошибка при изменении пароля.'
            form_name = 'pwd_form'

        notify_error(self.request, message=message)

        return self.render_to_response(
            self.get_context_data(**{form_name:form}))
