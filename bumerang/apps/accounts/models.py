# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import warnings

from django.contrib.auth.models import (
    UserManager, AbstractBaseUser, PermissionsMixin, UserManager, AbstractUser)
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django.utils.http import urlquote
from django.core.mail import send_mail
from django.utils import timezone

from bumerang.apps.utils.functions import get_path
from bumerang.apps.utils.models import FileModelMixin
from bumerang.apps.utils.media_storage import media_storage


nullable = dict(null=True, blank=True)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'),
                                      _('Enter a valid username.'), 'invalid')
        ])
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def get_profile(self):
        """
        Returns site-specific profile for this user. Raises
        SiteProfileNotAvailable if this site does not allow profiles.
        """
        warnings.warn("The use of AUTH_PROFILE_MODULE to define user profiles has been deprecated.",
            DeprecationWarning, stacklevel=2)
        if not hasattr(self, '_profile_cache'):
            from django.conf import settings
            if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
                raise SiteProfileNotAvailable(
                    'You need to set AUTH_PROFILE_MODULE in your project '
                    'settings')
            try:
                app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
            except ValueError:
                raise SiteProfileNotAvailable(
                    'app_label and model_name should be separated by a dot in '
                    'the AUTH_PROFILE_MODULE setting')
            try:
                model = models.get_model(app_label, model_name)
                if model is None:
                    raise SiteProfileNotAvailable(
                        'Unable to load the profile model, check '
                        'AUTH_PROFILE_MODULE in your project settings')
                self._profile_cache = model._default_manager.using(
                                   self._state.db).get(user__id__exact=self.id)
                self._profile_cache.user = self
            except (ImportError, ImproperlyConfigured):
                raise SiteProfileNotAvailable
        return self._profile_cache

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        db_table = 'auth_user'
        abstract = False
        app_label = 'auth'
        verbose_name = _('user')
        verbose_name_plural = _('users')


class Profile(FileModelMixin, User):
    # User types constants
    TYPE_USER = 1
    TYPE_SCHOOL = 2
    TYPE_STUDIO = 3
    TYPE_FESTIVAL = 4

    ACCOUNT_TYPES = (
        (TYPE_USER,      u'Независимый участник'),
        (TYPE_SCHOOL,    u'Школа'),
        (TYPE_STUDIO,    u'Студия'),
        #(TYPE_FESTIVAL,  u'Фестиваль'),
    )

    GENDER = (
        (1, u'Мужской'),
        (2, u'Женский'),
    )

    RESUME_FIELDS_GROUPS = [
        (u'Работа и карьера', ['work_type', 'work_company']),
        (u'Образование', ['schools', 'courses']),
        (u'Интересы', ['hobby', 'fav_movies', 'fav_music', 'fav_books'])
    ]
    title = models.CharField(u'Название/ФИО', max_length=255, **nullable)
    type = models.IntegerField(
        u'Тип профиля', choices=ACCOUNT_TYPES, default=1, db_index=True)
    avatar = models.ImageField(
        u'Фотография профиля',
        upload_to=get_path('avatars/{0}/full{1}', pk_dir_name=True),
        storage=media_storage, **nullable)
    min_avatar = models.ImageField(
        u'Уменьшенная фотография профиля',
        upload_to=get_path('avatars/{0}/min{1}', pk_dir_name=True),
        storage=media_storage, **nullable)
    avatar_coords = models.CharField(max_length=255, **nullable)
    birthday = models.DateField(u'День рождения', **nullable)
    description = models.TextField(u'Описание', **nullable)
    friends_count = models.IntegerField(u'Друзей', default=0, editable=False)
    activation_code = models.CharField(max_length=32, editable=False,
                                       **nullable)
    activation_code_expire = models.DateTimeField(editable=False, **nullable)

    # Специфические для разных типов пользователей поля
    country = models.CharField(u'Страна', max_length=255, **nullable)
    region = models.CharField(u'Регион', max_length=255, **nullable)
    city = models.CharField(u'Город', max_length=255, **nullable)
    work_type = models.TextField(u'Род деятельности', **nullable)
    work_company = models.TextField(u'Компания', **nullable)
    schools = models.TextField(u'Учебные заведения, специальность', **nullable)
    courses = models.TextField(u'Учебные курсы, сертификаты', **nullable)
    hobby = models.TextField(u'Увлечения и хобби', **nullable)
    fav_movies = models.TextField(u'Любимые фильмы и передачи', **nullable)
    fav_music = models.TextField(u'Любимая музыка', **nullable)
    fav_books = models.TextField(u'Любимые книги', **nullable)

    nickname = models.CharField(u'Никнейм', max_length=100, **nullable)
    gender = models.IntegerField(u'Пол', choices=GENDER, **nullable)

    info_name = models.CharField(
        u'Имя', max_length=100, blank=False, null=True)
    info_second_name = models.CharField(
        u'Фамилия', max_length=100, blank=False, null=True)
    info_middle_name = models.CharField(
        u'Отчество', max_length=100, blank=False, null=True)
    info_address = models.TextField(u'Фактический адрес')
    info_postal_address = models.TextField(u'Почтовый адрес')
    info_phone = models.CharField(u'Контактный телефон', max_length=40)
    info_mobile_phone = models.CharField(
        u'Мобильный телефон', max_length=12, **nullable)
    info_email = models.EmailField(u'Электронный адрес')
    info_organization = models.CharField(
        u'Название организации', max_length=255)
    info_organization_form = models.CharField(
        u'Организационно-правовая форма', max_length=255)

    views_count = models.IntegerField(
        u'Количество просмотров профиля', default=0, editable=False, **nullable)

    objects = UserManager()

    def __unicode__(self):
        return self.title or self.username

    def get_title(self):
        u"""
        Возвращает строку для формирования заголовка страницы
        в формате "<пользователя, школы, etc> %title%"
        """
        title = str()
        if self.type == self.TYPE_USER:
            title = u'пользователя'
        if self.type == self.TYPE_SCHOOL:
            title = u'школы'
        if self.type == self.TYPE_STUDIO:
            title = u'студии'

        return u'{0} {1}'.format(title, self.title)

    def get_info_fio(self):
        return ' '.join([getattr(self, name) for name in [
            'info_second_name', 'info_name', 'info_middle_name']
                         if getattr(self, name)])

    def get_locality(self):
        u"""
        Возвращает строку для поля "откуда" профиля
        """
        return ", ".join([s for s in self.country, self.region, self.city if s])

    def get_fields_group(self, field_names):
        u"""
        Принимает список полей, проверяет, возвращает список словарей
        {'name': <имя поля>, 'value':<значение>} для заполненных полей
        """
        field_names = set(field_names) & set(self._meta.get_all_field_names())
        return [{
            'name': self._meta.get_field(field).verbose_name,
            'value': getattr(self, field)}
            for field in field_names if getattr(self, field, None)]

    def get_user_profile_resume(self):
        return [{'name': label, 'values': self.get_fields_group(fields)}
                for label, fields in self.RESUME_FIELDS_GROUPS
                if self.get_fields_group(fields)]

    def get_studio_profile_resume(self):
        services_list = [{'name': obj.title, 'value': obj.description}
                         for obj in self.service_set.all().order_by('id')]
        if services_list:
            return [{'name': u'Услуги', 'values': services_list}]
        return []

    def get_school_profile_resume(self):
        services_list = [{'name': obj.title, 'value': obj.description}
                         for obj in self.faculty_set.all().order_by('id')]
        if services_list:
            return [{'name': u'Факультеты', 'values': services_list}]
        return []

    def videos_without_album(self):
        return self.video_set.filter(album__isnull=True)

    def photos_without_album(self):
        return self.photo_set.filter(album__isnull=True)

    def inbox_count(self):
        self.received_messages.filter(
            read_at__isnull=True, recipient_deleted_at__isnull=True).count()

    def show_avatar(self):
        if self.min_avatar:
            return u'<img src="{0}"/>'.format(self.min_avatar)
        return None
    show_avatar.short_description = u'Аватарка'
    show_avatar.allow_tags = True


class Faculty(models.Model):
    title = models.CharField(u'Название', max_length=255, blank=False)
    description = models.TextField(u'Описание')
    owner = models.ForeignKey(Profile, verbose_name=u'Факультеты',)

    def __unicode__(self):
        return self.title


class Service(models.Model):
    title = models.CharField(u'Название', max_length=255, blank=False)
    description = models.TextField(u'Описание')
    owner = models.ForeignKey(Profile, verbose_name=u'Услуги')

    def __unicode__(self):
        return self.title


class Teammate(FileModelMixin, models.Model):
    photo = models.ImageField(
        u'Фотография', storage=media_storage,
        upload_to=get_path('teammates/{0}/full{1}', pk_dir_name=True))
    photo_min = models.ImageField(
        u'Миниатюрная фотография', storage=media_storage, blank=True,
        upload_to=get_path('teammates/{0}/min{1}', pk_dir_name=True))
    name = models.CharField(u'Имя', max_length=255)
    description = models.TextField(u'Описание')
    owner = models.ForeignKey(Profile, verbose_name=u'Команда',)

    def __unicode__(self):
        return self.name


class Teacher(FileModelMixin, models.Model):
    photo = models.ImageField(
        u'Фотография', storage=media_storage,
        upload_to=get_path('teachers/{0}/full{1}', pk_dir_name=True))
    photo_min = models.ImageField(
        u'Миниатюрная фотография', storage=media_storage, blank=True,
        upload_to=get_path('teachers/{0}/min{1}', pk_dir_name=True))
    name = models.CharField(u'Имя', max_length=255)
    description = models.TextField(u'Описание')
    owner = models.ForeignKey(Profile, verbose_name=u'Команда')

    def __unicode__(self):
        return self.name
