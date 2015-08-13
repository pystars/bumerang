# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Max, Sum
from django.utils.timezone import now, UTC

from bumerang.apps.utils.models import TitleUnicode, nullable
from bumerang.apps.video.models import Video


class Channel(models.Model, TitleUnicode):
    site = models.ForeignKey(Site, default=1)
    title = models.CharField(
        u'Канал вещания', max_length=255,
        help_text=u'Например "главная страница"')
    slug = models.SlugField(max_length=255)

    class Meta:
        verbose_name = u'Канал вещания'
        verbose_name_plural = u'Каналы вещания'


class PlayList(models.Model):
    DURATION_CHOICES = (
        (3, u'3 часа'),
        (4, u'4 часа'),
        (6, u'6 часов'),
        (12, u'12 часов'),
        (24, u'24 часа'),
    )

    channel = models.ForeignKey(Channel)
    rotate_from_date = models.DateField(u'Дата начала ротации')
    created = models.DateTimeField(
        u'Время создания', default=now, editable=False)
    duration = models.PositiveSmallIntegerField(
        u'Длительность в часах', default=24,
        help_text=u'позволяет задать длительность цикла воспроизведения.',
        choices=DURATION_CHOICES
    )

    class Meta:
        verbose_name = u'Список воспроизведения'
        verbose_name_plural = u'Списки воспроизведения'
        ordering = ['-rotate_from_date', '-id']
        unique_together = ['channel', 'rotate_from_date']

    def __unicode__(self):
        try:
            return u'{0}:{1}'.format(
                self.channel.title, self.rotate_from)
        except Channel.DoesNotExist:
            return None

    @property
    def rotate_from(self):
        return self.rotate_from_date
        # year, month, day = self.rotate_from_date.timetuple()[0:3]
        # d = settings.PLAYLIST_START_TIME_SHIFT
        # td = timedelta(days=d['days'], hours=d['hours'])
        # return datetime(year, month, day, tzinfo=UTC()) + td

    def cycles_count(self):
        return 24 / self.duration

    def cycles(self):
        return range(self.cycles_count())

    def blocks(self):
        for cycle in self.cycles():
            for block in self.playlistblock_set.all():
                block.cycle = cycle
                yield block

    def get_first_item(self):
        items = list(PlayListItem.objects.filter(
            block__in=self.playlistblock_set.all())[:1])
        if items:
            return items[0]
        return None


class PlayListBlock(models.Model, TitleUnicode):
    cycle = 0
    playlist = models.ForeignKey(PlayList)
    title = models.CharField(u'Название блока', max_length=100)
    sort_order = models.PositiveSmallIntegerField(
        u'Порядок сортировки', null=True)
    limit = models.PositiveSmallIntegerField(
        u'Лимит времени', help_text=u'В минутах', default=24 * 60)

    class Meta:
        verbose_name = u'Блок списка воспроизведения'
        verbose_name_plural = u'Блоки списков воспроизведения'
        ordering = ['sort_order']

    def duration(self):
        return self.playlistitem_set.aggregate(
            s=Sum('video__duration'))['s'] or 0

    def block_offset(self):
        # returns Sum of previous block's limits, returns minutes
        return self.playlist.playlistblock_set.filter(
            sort_order__lt=self.sort_order).aggregate(s=Sum('limit'))['s'] or 0

    def offset(self):
        # in minutes
        return self.cycle * self.playlist.duration + self.block_offset()

    @property
    def rotate_from(self):
        return self.playlist.rotate_from

    def save(self, *args, **kwargs):
        if self.sort_order is None:
            self.sort_order = self.playlist.playlistblock_set.aggregate(
                Max('sort_order'))['sort_order__max'] or 0 + 1
        return super(PlayListBlock, self).save(*args, **kwargs)

    def is_full(self):
        return self.duration() > self.limit * 60000


class PlayListItem(models.Model, TitleUnicode):
    video = models.ForeignKey(Video, on_delete=models.PROTECT)
    block = models.ForeignKey(PlayListBlock)
    offset = models.IntegerField(
        u'Отсрочка воспроизведения', null=True, help_text=u'в миллисекундах')
    sort_order = models.IntegerField(u'порядок сортировки', **nullable)

    class Meta:
        ordering = ['sort_order']

    def save(self, *args, **kwargs):
        if self.sort_order is None:
            self.sort_order = self.block.playlistitem_set.aggregate(
                Max('sort_order'))['sort_order__max'] or 0 + 1
        return super(PlayListItem, self).save(*args, **kwargs)

    def play_from(self):
        # in seconds from begin of date
        return self.block.offset() * 60 + self.offset / 1000
        # return self.block.rotate_from + timedelta(milliseconds=self.offset)

    def play_till(self):
        return self.play_from() + self.video.duration / 1000
        # return self.play_from() + timedelta(milliseconds=self.video.duration)

    @property
    def title(self):
        return self.video.title
