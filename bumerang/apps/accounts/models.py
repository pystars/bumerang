# -*- coding: utf-8 -*-
import os

from django.contrib.auth.models import User, UserManager
from django.db import models

import bumerang.settings as settings

nullable = dict(null=True, blank=True)

def get_avatar_path(instance, filename):
    path = os.path.join(settings.MEDIA_ROOT, 'avatars', str(instance.id))
    if not os.path.exists(path):
        os.makedirs(path)
    ext = os.path.splitext(filename)[1]
    return 'avatars/{0}/full{1}'.format(instance.id, ext)

def get_mini_avatar_path(instance, filename):
    path = os.path.join(settings.MEDIA_ROOT, 'avatars', str(instance.id))
    if not os.path.exists(path):
        os.makedirs(path)
    ext = os.path.splitext(filename)[1]
    return 'avatars/{0}/min{1}'.format(instance.id, ext)


class Profile(User):
    ACCOUNT_TYPES = (
        (1, u'Независимый участник'),
        (2, u'Школа'),
        (3, u'Студия'),
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

    type = models.IntegerField(u'Тип профиля', choices=ACCOUNT_TYPES, default=1,
                               db_index=True)
    title = models.CharField(u'Название/Никнейм', max_length=255, **nullable)
    avatar = models.ImageField(u'Фотография профиля',
        upload_to=get_avatar_path, **nullable)
    min_avatar = models.ImageField(u'Уменьшенная фотография профиля',
        upload_to=get_mini_avatar_path, **nullable)
    avatar_coords = models.CharField(max_length=255, **nullable)
#    place = models.CharField(u'Откуда', max_length=255, **nullable)
    birthday = models.DateField(u'День рождения', **nullable)
    description = models.TextField(u'Описание', **nullable)
    views_count = models.IntegerField(u'Просмотров', default=0, editable=False)
    friends_count = models.IntegerField(u'Друзей', default=0, editable=False)
    activation_code = models.CharField(max_length=32, editable=False,
                                       **nullable)
    activation_code_expire = models.DateTimeField(editable=False, **nullable)

    # Специфические для разных типов пользователей поля
#    work = models.TextField(u'Работа и карьера', **nullable)
#    education = models.TextField(u'Образование', **nullable)
#    interests = models.TextField(u'Интересы', **nullable)
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

    # Школа
#    teachers = models.ManyToManyField('self', through='TeachersRelationship',
#                                      verbose_name=u'Преподаватели',
#                                      related_name='teacher_related_to',
#                                      symmetrical=False,
#                                      **nullable)

    #Студия
#    services = models.CharField(u'Услуги', max_length=255, **nullable)
#    team = models.ManyToManyField('self', verbose_name=u'Команда', **nullable)

    views_count = models.IntegerField(u'Количество просмотров профиля',
                                      default=0,
                                      editable=False, **nullable)

    objects = UserManager()

    def __unicode__(self):
        return self.email

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


class Teammate(models.Model):
    photo = models.ImageField(u'Фотография', upload_to='teams')
    name = models.CharField(u'Имя', max_length=255)
    description = models.TextField(u'Описание')
    owner = models.ForeignKey(Profile, verbose_name=u'Команда',)

    def __unicode__(self):
        return self.name


class Teacher(models.Model):
    photo = models.ImageField(u'Фотография', upload_to='teachers')
    name = models.CharField(u'Имя', max_length=255)
    description = models.TextField(u'Описание')
    owner = models.ForeignKey(Profile, verbose_name=u'Команда',)

    def __unicode__(self):
        return self.name
