# -*- coding: utf-8 -*-
import os

from django.contrib.auth.models import User, UserManager
from django.db import models

import settings

nullable = dict(null=True, blank=True)

def get_avatar_path(instance, filename):
    path = os.path.join(settings.MEDIA_ROOT, 'avatars', str(instance.id))
    if not os.path.exists(path):
        os.makedirs(path)
    return 'avatars/{0}/full{1}'.format(
        str(instance.id), os.path.splitext(filename)[1])

def get_mini_avatar_path(instance, filename):
    path = os.path.join(settings.MEDIA_ROOT, 'avatars', str(instance.id))
    if not os.path.exists(path):
        os.makedirs(path)
    return 'avatars/{0}/min{1}'.format(
        str(instance.id), os.path.splitext(filename)[1])


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

    type = models.IntegerField(u'Тип профиля', choices=ACCOUNT_TYPES, default=1,
                               db_index=True)
    title = models.CharField(u'Название/Никнейм', max_length=255, **nullable)
    avatar = models.ImageField(u'Фотография профиля',
        upload_to=get_avatar_path, **nullable)
    min_avatar = models.ImageField(u'Уменьшенная фотография профиля',
        upload_to=get_mini_avatar_path, **nullable)
    avatar_coords = models.CharField(max_length=255, **nullable)
    place = models.CharField(u'Откуда', max_length=255, **nullable)
    birthday = models.DateField(u'День рождения', **nullable)
    description = models.TextField(u'Описание', **nullable)
    views_count = models.IntegerField(u'Просмотров', default=0, editable=False)
    friends_count = models.IntegerField(u'Друзей', default=0, editable=False)
    activation_code = models.CharField(max_length=32, editable=False,
                                       **nullable)

    '''
    Специфические для разных типов пользователей поля
    '''
    # Независимый участник
#    work = models.TextField(u'Работа и карьера', **nullable)
#    education = models.TextField(u'Образование', **nullable)
#    interests = models.TextField(u'Интересы', **nullable)
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
    teachers = models.ManyToManyField('self', through='TeachersRelationship',
                                      verbose_name=u'Преподаватели',
                                      related_name='teacher_related_to',
                                      symmetrical=False,
                                      **nullable)

    #Студия
#    services = models.CharField(u'Услуги', max_length=255, **nullable)
    team = models.ManyToManyField('self', verbose_name=u'Команда', **nullable)

    objects = UserManager()

    def __unicode__(self):
        return self.email


REL_TEACHER_REQUEST = 1
REL_TEACHER_ACCEPTED = 2
REL_TEACHER_STATUSES = (
    (REL_TEACHER_REQUEST, u'Запрос отправлен'),
    (REL_TEACHER_ACCEPTED, u'Запрос принят'),
)


class TeachersRelationship(models.Model):
    from_profile = models.ForeignKey(Profile, related_name='from_profile')
    to_profile = models.ForeignKey(Profile, related_name='to_profile')
    status = models.IntegerField(choices=REL_TEACHER_STATUSES)


class Faculty(models.Model):
    title = models.CharField(u'Название', max_length=255, blank=False)
    description = models.TextField(u'Описание', blank=False)
    owner = models.ForeignKey(Profile, verbose_name=u'Факультеты',)

    def __unicode__(self):
        return self.title

class Service(models.Model):
    title = models.CharField(u'Название', max_length=255, blank=False)
    description = models.TextField(u'Описание', blank=False)
    owner = models.ForeignKey(Profile, verbose_name=u'Услуги')

    def __unicode__(self):
        return self.title