# -*- coding: utf-8 -*-
from django.db.models.query import QuerySet
import os
from datetime import timedelta, datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from apps.video.mediainfo import ExecutionError

from mediainfo import get_metadata

nullable = dict(null=True, blank=True)

class VideoAlbum(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(u'Название', max_length=100)
    description = models.TextField(u'Описание')
    cover = models.OneToOneField('Video', on_delete=models.SET_NULL, **nullable)

    class Meta:
        verbose_name = u'Видеоальбом'
        verbose_name_plural = u'Видеоальбомы'

    def __unicode__(self):
        return u'{0}'.format(self.title)

    def preview(self):
        if self.cover:
            return self.cover.preview
        return None


class VideoCategory(models.Model):
    title = models.CharField(max_length=255, verbose_name=u"Имя")
    slug = models.SlugField()

    def __unicode__(self):
        return u'{0}'.format(self.title)

    class Meta:
        verbose_name = u'Категория видео'
        verbose_name_plural = u'Категории видео'


class VideoGenre(models.Model):
    title = models.CharField(max_length=255, verbose_name=u"Имя")
    slug = models.SlugField()

    def __unicode__(self):
        return u'{0}'.format(self.title)

    class Meta:
        verbose_name = u'Жанр видео'
        verbose_name_plural = u'Жанры видео'


class VideoManager(models.Manager):
    def get_query_set(self):
        return super(VideoManager, self).get_query_set().filter(blocked=False)

class Video(models.Model):
    ACCESS_FLAGS = (
        (1, u'Всем пользователям'),
        (2, u'Пользователем, у которых есть ссылка'),
        (3, u'Пользователем, у которых есть ссылка и пароль'),
        (4, u'Друзьям'),
        (5, u'Только мне'),
    )

    published_in_archive = models.BooleanField(u'Опубликовано в видеорхиве',
        default=False)
    blocked = models.BooleanField(u'Заблокированно', default=False)
    is_in_broadcast_lists = models.BooleanField(u'Списки вещания',
        default=False)

    title = models.CharField(u'Название', max_length=255)
    slug = models.SlugField(u'Метка (часть ссылки)', **nullable)
    original_file = models.FileField(u"Оригинальное видео",
        upload_to='videos/originals', **nullable)
    hq_file = models.FileField(u'Видео высокого качества',
        upload_to='videos/high', **nullable)
    mq_file = models.FileField(u'Видео среднего качества',
        upload_to='videos/medium', **nullable)
    lq_file = models.FileField(u'Видео низкого качества',
        upload_to='videos/low', **nullable)
    preview = models.FileField(u'Превью',
        upload_to='videos/previews', **nullable)
    duration = models.IntegerField(u'Длительность', editable=False, **nullable)
    owner = models.ForeignKey(User, verbose_name=u"Владелец")
    album = models.ForeignKey(VideoAlbum, verbose_name=u'Альбом',
        max_length=255, **nullable)
    category = models.ForeignKey(VideoCategory, verbose_name=u'Категория',
        **nullable)
    description = models.TextField(u'Описание', **nullable)
    year = models.IntegerField(u'Год', default=2011, **nullable)
    genre = models.ForeignKey(VideoGenre, verbose_name=u'Жанр', **nullable)
    country = models.CharField(u'Страна', max_length=255, **nullable)
    city = models.CharField(u'Город', max_length=255, **nullable)
    authors = models.CharField(u'Авторы', max_length=255, **nullable)
    agency = models.CharField(u'учреждение', max_length=255, **nullable)
    teachers = models.CharField(u'Педагоги', max_length=255, **nullable)
    manager = models.CharField(u'Руководитель', max_length=255, **nullable)
    festivals = models.TextField(u'Фестивали', **nullable)
    access = models.IntegerField(u'Кому доступно видео', choices=ACCESS_FLAGS,
        default=1, **nullable)
    created = models.DateTimeField(u'Дата добавления', default=datetime.now)

    # Кастомный менеджер объектов
    video_objects = VideoManager()

    class Meta:
        verbose_name = u'Видео'
        verbose_name_plural = u'Видео'
        ordering = ('-id',)

    def __unicode__(self):
        return u'{0}'.format(self.title)

    def save(self, *args, **kwargs):
        query = {
            'Video' : {
                'Duration' : int,
                }
        }
        file_field = self.best_quality_file() or self.original_file
        try:
            minfo = get_metadata(file_field.path, **query)
            self.duration = minfo['Video']['Duration']
        except ExecutionError:
            pass #TODO: remove it after tests
        super(Video, self).save(*args, **kwargs)
        if self.album:
            if not self.album.cover and self.preview:
                self.album.cover = self
                self.album.save()

    def delete(self, using=None):
        for field in self._meta.fields:
            if issubclass(field.__class__, models.FileField):
                file_field = getattr(self, field.name)
                #TODO: remove prints after tests
                try:
                    os.remove(file_field.path)
                    print 'deleted %s' % file_field.path
                except ValueError:
                    print 'no file specified with %s' % field.name
                except OSError:
                    print "can't remove file %s" % file_field.path
        super(Video, self).delete(using=using)

    def get_absolute_url(self):
        return reverse('video-detail', kwargs={'pk': self.pk})

    def best_quality_file(self):
        return self.hq_file or self.mq_file or self.lq_file or None

    def seconds_duration(self):
        return (self.duration or 0) / 1000


class Channel(models.Model):
    name = models.CharField(u'Канал вещания', max_length=255,
        help_text=u'Например "главная страница"')
    slug = models.SlugField(max_length=255)

    class Meta:
        verbose_name = u'Канал вещания'
        verbose_name = u'Каналы вещания'

    def __unicode__(self):
        return u'{0}'.format(self.name)


class PlayListItem(models.Model):
    video = models.ForeignKey(Video,
        limit_choices_to={'is_in_broadcast_lists': True})
    playlist = models.ForeignKey('PlayList')
    offset = models.IntegerField(
        u'Отсрочка со времени начала воспроизведения плейлиста', null=True)
    sort_order = models.IntegerField(u'порядок сортировки', **nullable)

    class Meta:
        ordering = ['sort_order', 'id']

    def play_from(self):
        return self.playlist.rotate_from + timedelta(milliseconds=self.offset)

    def play_till(self):
        return self.play_from() + timedelta(milliseconds=self.video.duration)

    def __unicode__(self):
        return u'{0}'.format(self.video.title)


class PlayList(models.Model):
    channel = models.ForeignKey(Channel)
    rotate_from = models.DateTimeField(u'Время начала ротации')
    rotate_till = models.DateTimeField(u'Время окончания ротации')
    created = models.DateTimeField(u'Дата создания',
        default=datetime.now, editable=False)

    class Meta:
        verbose_name = u'Список воспроизведения'
        verbose_name = u'Списки воспроизведения'
        ordering = ['rotate_till', 'id']

    def __unicode__(self):
        return u'{0}:{1}-{2}'.format(
            self.channel.name, self.rotate_from, self.rotate_till)
