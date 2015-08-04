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

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Раздел новостей'
        verbose_name_plural = u'Разделы новостей'
        unique_together = ('slug', 'site')
        ordering = ('sort_order', 'id')


class NewsItem(FileModelMixin, models.Model):
    category = models.ForeignKey(NewsCategory, related_name="news",
                                 verbose_name=u'Раздел новостей')
    title = models.CharField(max_length=255, verbose_name=u'Заголовок')
    slug = models.SlugField()
    preview_text = models.TextField(verbose_name=u'Текст превью')
    text = models.TextField(verbose_name=u'Текст')
    image = models.ImageField(
        u'Изображение', storage=media_storage, upload_to='news',
        help_text=u'Используется в списке новостей', **nullable)
    creation_date = models.DateTimeField(default=now)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Новость'
        verbose_name_plural = u'Новости'
        ordering = ('-creation_date',)
