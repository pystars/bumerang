# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, UserManager
from django.db import models


nullable = dict(null=True, blank=True)

def get_avatar_path(instance, filename):
    return filename


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

    type = models.IntegerField(u'Тип профиля', choices=ACCOUNT_TYPES, default=1)
    title = models.CharField(u'Название/Никнейм', max_length=255, **nullable)
    avatar = models.ImageField(u'Фотография профиля', upload_to='avatars', **nullable)
    e_mail = models.EmailField(u'E-mail', unique=True)
    place = models.CharField(u'Откуда', max_length=255, **nullable)
    birthday = models.DateField(u'День рождения', **nullable)
    description = models.TextField(u'Описание', **nullable)
    views_count = models.IntegerField(u'Просмотров', default=0, editable=False)
    friends_count = models.IntegerField(u'Друзей', default=0, editable=False)

    '''
    Специфические для разных типов пользователей поля
    '''
    # Независимый участник
    work = models.CharField(u'Работа и карьера', max_length=255, **nullable)
    education = models.CharField(u'Образование', max_length=255, **nullable)
    interests = models.CharField(u'Образование', max_length=255, **nullable)
    nickname = models.CharField(u'Никнейм', max_length=100, **nullable)
    gender = models.IntegerField(u'Пол', choices=GENDER, **nullable)

    # Школа
    faculties = models.CharField(u'Образование', max_length=255, **nullable)
    teachers = models.ForeignKey(User, verbose_name=u'Преподаватели', related_name='teachers', **nullable)

    #Студия
    services = models.CharField(u'Услуги', max_length=255, **nullable)
    team = models.ForeignKey(User, verbose_name=u'Команда', related_name='team', **nullable)

    objects = UserManager()
