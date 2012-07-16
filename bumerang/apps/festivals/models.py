# -*- coding: utf-8 -*-
import os

from django.db import models
from django.utils.timezone import now
from django.conf import settings

from bumerang.apps.accounts.models import Profile
from bumerang.apps.utils.media_storage import media_storage


nullable = dict(null=True, blank=True)

def get_logo_path(instance, filename):
    path = os.path.join(settings.MEDIA_ROOT, 'logos', str(instance.id))
    if not os.path.exists(path):
        os.makedirs(path)
    ext = os.path.splitext(filename)[1]
    return 'logos/{0}/full{1}'.format(instance.id, ext)

def get_mini_logo_path(instance, filename):
    path = os.path.join(settings.MEDIA_ROOT, 'logos', str(instance.id))
    if not os.path.exists(path):
        os.makedirs(path)
    ext = os.path.splitext(filename)[1]
    return 'logos/{0}/min{1}'.format(instance.id, ext)


class FestivalGroup(models.Model):
    owner = models.OneToOneField(Profile)
    name = models.CharField(u'Название группы фестивалей', max_length=255)

    class Meta:
        verbose_name = u'Группа фестивалей'
        verbose_name_plural = u'Группы фестивалей'


class Festival(models.Model):
    group = models.ForeignKey(FestivalGroup,
        verbose_name=u'Группа фестивалей')
    owner = models.ForeignKey(Profile)
    is_approved = models.BooleanField(u'Заявка подтверждена', default=False)

    logo = models.ImageField(u'Логотип фестиваля',
        upload_to=get_logo_path, storage=media_storage, **nullable)
    min_logo = models.ImageField(u'Уменьшенный логотип фестиваля',
        upload_to=get_mini_logo_path, storage=media_storage, **nullable)

    name = models.CharField(u'Название фестиваля', max_length=255)
    opened = models.BooleanField(u'Фестиваль открыт', default=True)
    start_date = models.DateField(u'Дата начала')
    end_date = models.DateField(u'Дата окончания')
    accept_requests_date = models.DateField(u'Прием заявок до')
    hold_place = models.TextField(u'Место проведения')
    description = models.TextField(u'Описание фестиваля')
    text_rules = models.TextField(u'Правила фестиваля', blank=False)
    file_rules = models.FileField(u'Правила фестиваля (документ)',
        upload_to='rules', blank=True)

    created = models.DateTimeField(u'Дата добавления', default=now,
        editable=False)

    def __unicode__(self):
        return self.name

    def is_accepting_requests(self):
        if self.accept_requests_date > now().date():
            return True
        return False

    class Meta:
        verbose_name = u'Фестиваль'
        verbose_name_plural = u'Фестивали'


class FestivalGeneralRule(models.Model):
    festival = models.ForeignKey(Festival, verbose_name=u'Фестиваль')

    title = models.CharField(u'Положение', max_length=255)
    description = models.TextField(u'Описание')

    class Meta:
        verbose_name = u'Общие положения'
        verbose_name_plural = verbose_name


class FestivalNomination(models.Model):
    festival = models.ForeignKey(Festival, verbose_name=u'Фестиваль')

    name = models.CharField(u'Название', max_length=255)
    description = models.CharField(u'Описание', max_length=255)

    class Meta:
        verbose_name = u'Номинация'
        verbose_name_plural = u'Номинации'