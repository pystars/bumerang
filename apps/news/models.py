# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models

class NewsCategory(models.Model):
    title = models.CharField(max_length=255, verbose_name=u'Название раздела')

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Раздел новостей'
        verbose_name_plural = u'Разделы новостей'


class NewsItem(models.Model):
    category = models.ForeignKey(NewsCategory, related_name="category", verbose_name=u'Раздел новостей')
    title = models.CharField(max_length=255, verbose_name=u'Заголовок')
    slug = models.SlugField()
    preview_text = models.TextField(verbose_name=u'Текст превью')
    text = models.TextField(verbose_name=u'Текст')
    creation_date = models.DateTimeField(editable=False, default=datetime.now())

    def __unicode__(self):
        return self.title

    class Meta:
        #app_label = u'Новости'
        verbose_name = u'Новость'
        verbose_name_plural = u'Новости'
