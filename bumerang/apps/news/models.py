# -*- coding: utf-8 -*-
from django.db import models
from django.utils.timezone import now
from django.contrib.sites.models import Site
from bumerang.apps.utils.media_storage import media_storage

from bumerang.apps.utils.models import FileModelMixin, nullable


class NewsCategory(models.Model):
    site = models.ForeignKey(Site, default=1)
    title = models.CharField(max_length=255, verbose_name=u'Название раздела')
    slug = models.SlugField()
    sort_order = models.IntegerField(default=0, verbose_name=u'Позиция')

    class Meta:
        verbose_name = u'Раздел новостей'
        verbose_name_plural = u'Разделы новостей'
        unique_together = ('slug', 'site')
        ordering = ('sort_order', 'id')

    def __unicode__(self):
        return u'{0}'.format(self.title)


class NewsItem(FileModelMixin, models.Model):
    category = models.ForeignKey(NewsCategory, related_name="news",
                                 verbose_name=u'Раздел новостей')
    title = models.CharField(max_length=255, verbose_name=u'Заголовок')
    slug = models.SlugField()
    preview_text = models.TextField(verbose_name=u'Текст превью')
    text = models.TextField(verbose_name=u'Текст', **nullable)
    image = models.ImageField(
        u'Квадратное изображение 80x80 пикселей', storage=media_storage,
        upload_to='news', help_text=u'Используется в списках', **nullable)
    creation_date = models.DateTimeField(default=now)

    class Meta:
        verbose_name = u'Новость'
        verbose_name_plural = u'Новости'
        ordering = ('-creation_date',)

    def __unicode__(self):
        return u'{0}'.format(self.title)


class NewsBlock(FileModelMixin, models.Model):
    owner = models.ForeignKey(NewsItem)
    text = models.TextField(verbose_name=u'Текст', **nullable)
    image = models.ImageField(
        u'Изображение', storage=media_storage, upload_to='news', **nullable)

    class Meta:
        verbose_name = u'Блок'
        verbose_name_plural = u'Блоки'
        ordering = ['id']

    def __unicode__(self):
        return u'{0}'.format(self.text)
