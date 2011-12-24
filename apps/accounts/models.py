# -*- coding: utf-8 -*-

from uuid import uuid4

from django.contrib.auth.models import User, UserManager
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

nullable = dict(null=True, blank=True)

class Profile(User):
    ACCOUNT_TYPES = (
        (1, u'Независимый участник'),
        (2, u'Школа'),
        (3, u'Студия'),
    )

    type = models.IntegerField(u'Тип профиля', choices=ACCOUNT_TYPES, default=1)
    title = models.CharField(u'Название/Никнейм', max_length=255, **nullable)
    e_mail = models.EmailField(u'E-mail', max_length=75, unique=True)
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
    inerests = models.CharField(u'Образование', max_length=255, **nullable)

    # Школа
    faculties = models.CharField(u'Образование', max_length=255, **nullable)
    teachers = models.ForeignKey(User, verbose_name=u'Преподаватели', related_name='teachers', **nullable)

    #Студия
    services = models.CharField(u'Услуги', max_length=255, **nullable)
    team = models.ForeignKey(User, verbose_name=u'Команда', related_name='team', **nullable)

    objects = UserManager()

@receiver(pre_save, sender=Profile)
def profile_pre_save_handler(sender, **kwargs):
    user = kwargs['instance']
    user.username = uuid4().get_hex()[:30]
    from django.contrib.auth.models import get_hexdigest
    import random
    algo = 'sha1'
    salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
    hsh = get_hexdigest(algo, salt, user.password)
    user.password = '%s$%s$%s' % (algo, salt, hsh)