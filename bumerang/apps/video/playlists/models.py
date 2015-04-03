# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from django.conf import settings
from django.db import models
from django.utils.timezone import now, UTC

from bumerang.apps.utils.models import TitleUnicode, nullable
from bumerang.apps.video.models import Video


class Channel(models.Model, TitleUnicode):
    title = models.CharField(u'Канал вещания', max_length=255,
        help_text=u'Например "главная страница"')
    slug = models.SlugField(max_length=255)

    class Meta:
        verbose_name = u'Канал вещания'
        verbose_name_plural = u'Каналы вещания'


class PlayListItem(models.Model, TitleUnicode):
    video = models.ForeignKey(Video,
        limit_choices_to={'is_in_broadcast_lists': True},
        on_delete=models.PROTECT)
    playlist = models.ForeignKey('PlayList')
    offset = models.IntegerField(u'Отсрочка воспроизведения', null=True,
        help_text=u'в миллисекундах')
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
    rotate_from_date = models.DateField(u'Дата начала ротации')
    created = models.DateTimeField(
        u'Время создания', default=now, editable=False)

    class Meta:
        verbose_name = u'Список воспроизведения'
        verbose_name_plural = u'Списки воспроизведения'
        ordering = ['rotate_from_date', 'id']
        unique_together = ['channel', 'rotate_from_date']

    def __unicode__(self):
        try:
            return u'{0}:{1}'.format(
                self.channel.title, self.rotate_from)
        except Channel.DoesNotExist:
            return None

    @property
    def rotate_from(self):
        year, month, day = self.rotate_from_date.timetuple()[0:3]
        d = settings.PLAYLIST_START_TIME_SHIFT
        td = timedelta(days=d['days'], hours=d['hours'])
        return datetime(year, month, day, tzinfo=UTC()) + td
