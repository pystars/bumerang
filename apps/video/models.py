# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class VideoCategory(models.Model):
    title = models.CharField(max_length=255, verbose_name="Имя")
    slug = models.SlugField()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Категория видео'
        verbose_name_plural = u'Категории видео'

class VideoGenre(models.Model):
    title = models.CharField(max_length=255, verbose_name="Имя")
    slug = models.SlugField()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Жанр видео'
        verbose_name_plural = u'Жанры видео'

class Video(models.Model):
    title = models.CharField(max_length=255, default='', verbose_name=u'Название')
    slug = models.SlugField(default='', blank=True, verbose_name=u'Ссылка на видео')

    #original_filename = models.CharField(max_length=512)

    video_file = models.FileField(upload_to='originals', verbose_name=u"Видео")

    #owner = models.ForeignKey(User, related_name="videos")
    owner = models.ForeignKey(User, related_name="videos", verbose_name=u"Владелец")

    broadcast_lists = models.CharField(max_length=255, default='', verbose_name=u'Списки вещания')

    album = models.CharField(max_length=255, default='', verbose_name=u'Альбом')

    category = models.ForeignKey(VideoCategory, related_name="videos", default=0, verbose_name=u'Категория')

    description = models.TextField(verbose_name=u'Описание')

    year = models.IntegerField(default=2011, verbose_name=u'Год')

    genre = models.ForeignKey(VideoGenre, related_name="videos", default=0, verbose_name=u'Жанр')

    country = models.CharField(max_length=255, default='', verbose_name=u'Страна')
    city = models.CharField(max_length=255, default='', verbose_name=u'Город')

    authors = models.CharField(max_length=255, default='', verbose_name=u'Авторы')
    teachers = models.CharField(max_length=255, default='', verbose_name=u'Педагоги')
    manager = models.CharField(max_length=255, default='', verbose_name=u'Руководитель')

    festivals = models.TextField(default='', verbose_name=u'Фестивали')

    ACCESS_FLAGS = (
        (1, 'All users'),
        (2, 'Users with link'),
        (3, 'Users with link and password'),
        (4, 'Friends'),
        (5, 'Only for me'),
    )

    access = models.IntegerField(choices=ACCESS_FLAGS, default=1, verbose_name=u'Кому доступно видео')

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Видео'
        verbose_name_plural = u'Видео'