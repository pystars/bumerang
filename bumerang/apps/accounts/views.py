# -*- coding: utf-8 -*-
from __future__ import division
import json
import urlparse
from datetime import timedelta
from uuid import uuid4
from bumerang.apps.festivals.models import Festival

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from PIL import Image
from django.contrib.auth.models import User
from django.forms.util import ErrorList
from django.db.models import F
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.sites.models import Site, get_current_site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.views.generic import CreateView, DetailView, TemplateView
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.forms.models import inlineformset_factory
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.utils.timezone import now

from bumerang.apps.utils.functions import random_string
from bumerang.apps.video.models import Video
from bumerang.apps.accounts.forms import (RegistrationForm,
      PasswordRecoveryForm, ProfileAvatarEditForm, ProfileEmailEditForm,
      UserProfileInfoForm, SchoolProfileInfoForm, StudioProfileInfoForm, UserContactsForm, OrganizationContactsForm, FestivalRegistrationRequestForm, FestivalProfileInfoForm)
from bumerang.apps.accounts.models import Profile
from bumerang.apps.utils.email import send_activation_success, send_activation_link, send_new_password, send_fest_registration_request
#from bumerang.apps.utils.tasks import (send_new_password_task,
#    send_activation_link_task)

# TODO: рефакторить нотификации

def notify_success(request, message):
    u"""
    Выводит уведомление об успешном сохранении информации профиля
    """
    request._messages._queued_messages = []
    messages.add_message(request, messages.SUCCESS, message)
    return

def notify_error(request, message):
    u"""
    Выводит уведомление об ошибке при сохранении информации профиля
    """
    request._messages._queued_messages = []
    messages.add_message(request, messages.ERROR, message)
    return

def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            netloc = urlparse.urlparse(redirect_to)[1]

            profile = Profile.objects.get(
                username=form.cleaned_data['username'])

            message = u'''
            Вы авторизованы. Пожалуйста, заполните имя вашего профиля.
            '''

            if profile.type == Profile.TYPE_USER:
                name = profile.nickname or profile.title
                if name:
                    message = u'''
                    Добро пожаловать, {0}. Вы авторизованы.
                    '''.format(name)

            if profile.type == Profile.TYPE_SCHOOL:
                if profile.title:
                    message = u'''
                    Добро пожаловать. Вы авторизовались как школа «{0}».
                    '''.format(profile.title)

            if profile.type == Profile.TYPE_STUDIO:
                if profile.title:
                    message = u'''
                    Добро пожаловать. Вы авторизовались как студия «{0}».
                    '''.format(profile.title)

            if profile.type == Profile.TYPE_FESTIVAL:
                if profile.title:
                    message = u'''
                    Добро пожаловать. Вы авторизовались как фестиваль «{0}».
                    '''.format(profile.title)

            notify_success(request, message)

            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = reverse('profile-detail', args=[profile.id])

            # Security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = reverse('BumerangIndexView')

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)

        else:
            notify_error(request, message=u'Неправильный логин или пароль.')

    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
        }
    context.update(extra_context or {})
    return render_to_response(template_name, context,
        context_instance=RequestContext(request, current_app=current_app))


class RegistrationFormView(CreateView):
    form_class = RegistrationForm
    template_name = "accounts/registration.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return super(RegistrationFormView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('BumerangIndexView'))

    def get_success_url(self):
        return reverse('BumerangIndexView')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.is_active = False

        # Festival user type
        if self.object.type == 4:
            self.object.save()
            send_fest_registration_request()

            self.request.session['fest_profile_id'] = self.object.id

            notify_success(self.request, message=u'''
                Заполните все поля чтобы отправить заявку
                 на рассмотрение
                ''')

            return HttpResponseRedirect(reverse('register-fest-request'))

        else:
            self.object.activation_code = random_string(32)

            current_site = Site.objects.get_current()
            url = reverse('activate-account', args=[self.object.activation_code])

            full_activation_url = 'http://{0}{1}'.format(current_site, url)
            self.object.activation_code_expire = now() + timedelta(days=1)
            self.object.save()

            send_activation_link(full_activation_url, form.cleaned_data['username'])

            notify_success(self.request, message=u'''
                Регистрация прошла успешно. Вам была отправлена ссылка
                для активации аккаунта.
                Проверьте почту и активируйте ваш аккаунт.
                ''')

        return super(RegistrationFormView, self).form_valid(form)

    def form_invalid(self, form):
        notify_error(self.request, message=u'При регистрации произошла ошибка.')

        return self.render_to_response(self.get_context_data(form=form))


class RegisterFestRequestForm(FormView):
    form_class = FestivalRegistrationRequestForm
    template_name = "accounts/regisration_festival_info_form.html"

    profile_id = None

    def _get_profile_id(self):
        return self.request.session.get('fest_profile_id')

    def get(self, request, *args, **kwargs):
        if self._get_profile_id():
            return super(RegisterFestRequestForm, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('registration'))

    def get_success_url(self):
        return reverse('BumerangIndexView')

    def get_form(self, form_class):
        return form_class(self.request.POST, instance=Profile.objects.get(id=self._get_profile_id()))

    def form_valid(self, form):
        form.save()

        notify_success(self.request, message=u'''
        Ваша заявка принята, мы с вами свяжемся.
        ''')

        return super(RegisterFestRequestForm, self).form_valid(form)


class AccountActivationView(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            user = Profile.objects.get(activation_code=kwargs['code'])

            if user.activation_code_expire < now():
                user.delete()

                notify_error(self.request, message=u'''
                    С момента регистрации прошло больше суток и активационная
                    ссылка устарела.
                    Пройдите процедуру <a href="{0}">регистрации</a> заново.
                '''.format(reverse('registration')))

                return HttpResponseRedirect(reverse('BumerangIndexView'))

            user.is_active = True
            user.activation_code = ''
            user.save()
            notify_success(self.request, message=u'''
                Ваш аккаунт успешно активирован.
                Теперь вы можете <a href="{0}">войти</a> в систему.
            '''.format(reverse('login')))

            send_activation_success(user.username)

            return HttpResponseRedirect(reverse('BumerangIndexView'))

        except Profile.DoesNotExist:
            notify_error(self.request, message=u'''
                При активации аккаунта произошла ошибка.
                Возможно, аккаунт уже был активирован ранее,
                либо срок действия ссылки истёк.
            ''')

            return HttpResponseRedirect(reverse('BumerangIndexView'))


class PasswordRecoveryView(FormView):
    form_class = PasswordRecoveryForm
    template_name = "accounts/password_recovery.html"

    def get_success_url(self):
        return '/'

    def form_valid(self, form):
        receiver_email = form.data['email']
        new_password = uuid4().get_hex()[:8]
        profile = Profile.objects.get(email=receiver_email)
        profile.set_password(new_password)
        profile.save()

        send_new_password(new_password, receiver_email)
        notify_success(self.request, message=u'''
            Ваш новый пароль был отправлен на указанный вами e-mail.
            После авторизации вы сможете его сменить в разделе
            редактирования профиля.
        ''')

        return HttpResponseRedirect(self.get_success_url())


class ProfileView(DetailView):
    model = Profile

    def get_context_data(self, **kwargs):
        ctx = super(ProfileView, self).get_context_data(**kwargs)
        ctx.update({
            'hide_show_profile_link': True,
        })

        return ctx

    def get_object(self, queryset=None):
        if 'pk' not in self.kwargs:
            return self.request.user.profile
        return super(ProfileView, self).get_object(queryset=queryset)

    def get(self, request, **kwargs):
        response = super(ProfileView, self).get(request, **kwargs)
        if not self.object.id == getattr(request.user, 'id', None):
            Profile.objects.filter(pk=self.object.id).update(
                views_count=F('views_count') + 1)

        return response


class ProfileVideoView(DetailView):
    model = Profile

    def get_context_data(self, **kwargs):
        videos = self.object.videos_without_album()
        if not self.request.user.id == self.object.id:
            videos = videos.filter(status=Video.READY)
        ctx = super(ProfileVideoView, self).get_context_data(**kwargs)
        ctx['videos'] = videos
        return ctx


class ProfilePhotoView(DetailView):
    model = Profile

    def get_context_data(self, **kwargs):
        ctx = super(ProfilePhotoView, self).get_context_data(**kwargs)
        ctx['photos'] = self.object.photos_without_album()
        return ctx


class UsersListView(ListView):
    model = Profile
    paginate_by = 25

    def get_queryset(self):
        qs = super(UsersListView, self).get_queryset()
        if 'type' in self.kwargs:
            qs = qs.filter(type=self.kwargs['type'])
        return qs.filter(is_active=True, title__isnull=False).order_by('-id')

    def get_context_data(self, **kwargs):
        ctx = super(UsersListView, self).get_context_data(**kwargs)
        if 'type' in self.kwargs:
            ctx.update({'current_type': self.kwargs['type']})
        return ctx


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
        if self.request.user.profile.type == 4:
            return FestivalProfileInfoForm

    def get_success_url(self):
        return reverse("profile-detail", args=[self.get_object().id])

    def form_valid(self, form):
        self.object = form.save()
        notify_success(self.request,
            message=u'Информация вашего профиля успешно обновлена.')

        return super(ProfileInfoEditView, self).form_valid(form)

    def form_invalid(self, form):
        notify_error(self.request,
            message=u'При обновлении данных профиля произошла ошибка.')

        return self.render_to_response(self.get_context_data(form=form))


class ProfileUpdateView(UpdateView):
    model = Profile

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        notify_success(self.request, message=u'''
            Информация вашего профиля успешно обновлена.<br/>
            <a href="{0}">Перейти к просмотру профиля</a>
        '''.format(reverse("profile-detail", args=[self.get_object().id])))

        return super(ProfileUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        notify_error(self.request,
            message=u'При обновлении данных профиля произошла ошибка.')

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
        formset = self.FormSet(request.POST,request.FILES, instance=self.get_object())

        if formset.is_valid():
            formset.save()
            notify_success(self.request, message=u'''
                Информация вашего профиля успешно обновлена.<br/>
                 <a href="{0}">Перейти к просмотру профиля</a>
            '''.format(reverse("profile-detail", args=[self.get_object().id])))

            return HttpResponseRedirect(self.get_success_url())
        else:
            self.object = self.get_object()
            notify_error(self.request, message=u'''
                При обновлении данных профиля произошла ошибка.
            ''')

            return self.render_to_response(self.get_context_data(formset=formset))


class ProfileAvatarEditView(UpdateView):
    model = Profile
    form_class = ProfileAvatarEditForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse('profile-edit-avatar')

    def form_valid(self, form):
        u"""
        MAX_WIDTH - Эта константа означает максимальную ширину изображения так
        как будучи большим, оно может выйти за рамки шаблона. Если исходное
        изображение шире этой константы, оно будет ужато для обеспечения
        совместимости координат, переданных Crop'ом
        """
        MAX_WIDTH = 500
        try:
            coords = json.loads(form.cleaned_data['avatar_coords'])
        except ValueError:
            coords = {
                'x': 0,
                'y': 0,
                'x2': 175,
                'y2': 175,
            }
        # Загружен ли уже аватар и мы только должны его обрезать?
        img = Image.open(self.request.FILES.get('avatar', self.object.avatar))
        img = img.convert('RGB')

        # Если загружаемый аватар слишком маленький
        if img.size[0] < 175 or img.size[1] < 175:
            form_errors = form._errors.setdefault('avatar', ErrorList())
            form_errors.append(
            u'Размер изображения должен быть больше 175x175 пикселей.')

            notify_error(self.request, message=u'''
            Произошла ошибка при обновлении фотографии профиля.
            Размер изображения должен быть больше 175x175 пикселей.''')
            return self.render_to_response(self.get_context_data(form=form))

        # Если изображение слишком широкое, ужимаем
        if img.size[0] > MAX_WIDTH:
            aspect = img.size[0] / MAX_WIDTH
            new_height = int(round(img.size[1] / aspect))
            # Вот с этим изображением мы и будем работать
            img = img.resize((MAX_WIDTH, new_height), Image.ANTIALIAS)

        # Иначе просто обрезаем
        cropped_image = img.crop((coords['x'],
                                  coords['y'],
                                  coords['x2'],
                                  coords['y2']))
        cropped_image.thumbnail((175, 175), Image.ANTIALIAS)

        temp_handle = StringIO()
        cropped_image.save(temp_handle, 'jpeg', quality=100)
        temp_handle.seek(0)

        suf = SimpleUploadedFile('min.jpg',
            temp_handle.read(), content_type='image/jpg')

        self.object.min_avatar.save('min.jpg', suf, save=False)
        form.save()

        notify_success(self.request,
            message=u'Фотография профиля успешно обновлена.')

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        notify_error(self.request, message=u'''
            Произошла ошибка при обновлении фотографии профиля.
            Возможно, файл, который вы загрузили, поврежден
            или не является изображением.
        ''')

        return self.render_to_response(self.get_context_data(form=form))


class ProfileContactsEditView(UpdateView):
    model = Profile
    template_name = 'accounts/profile_edit_contacts.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_form_class(self):
        if self.request.user.profile.type == 1:
            return UserContactsForm
        else:
            return OrganizationContactsForm

    def get_success_url(self):
        return reverse('profile-edit-contacts')

    def form_valid(self, form):
        message = u'Контакты обновлены успешно.'
        notify_success(self.request, message=message)
        return super(ProfileContactsEditView, self).form_valid(form)

    def form_invalid(self, form):
        message = u'Ошибка при обновлении контактов.'
        notify_error(self.request, message=message)
        return super(ProfileContactsEditView, self).form_invalid(form)


class ProfileSettingsEditView(UpdateView):
    model = User
    email_form_class = ProfileEmailEditForm
    pwd_form_class = PasswordChangeForm
    template_name = "accounts/profile_edit_settings.html"

    def get_context_data(self, **kwargs):
        ctx = super(ProfileSettingsEditView, self).get_context_data(**kwargs)
        ctx.update({
            'profile': self.request.user.profile,
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


class ProfileFestivalListView(DetailView):
    model = Profile
    template_name = "accounts/profile_festival_list.html"

    def get_context_data(self, **kwargs):
        festivals = self.object.festival_set.all()
        ctx = super(ProfileFestivalListView, self).get_context_data(**kwargs)
        ctx['festivals'] = festivals
        return ctx