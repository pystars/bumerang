# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from django.db import models

from bumerang.apps.utils.models import TitleUnicode, nullable
from bumerang.apps.video.models import Video


class Channel(models.Model, TitleUnicode):
    title = models.CharField(u'Канал вещания', max_length=255,
        help_text=u'Например "главная страница"')
    slug = models.SlugField(max_length=255)

    class Meta:
        verbose_name = u'Канал вещания'
        verbose_name = u'Каналы вещания'


class PlayListItem(models.Model, TitleUnicode):
    video = models.ForeignKey(Video,
        limit_choices_to={'is_in_broadcast_lists': True},
        on_delete=models.PROTECT)
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

    @property
    def title(self):
        return self.video.title


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
            self.channel.title, self.rotate_from, self.rotate_till)
