# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models

class NewsItem(models.Model):
    title = models.CharField(max_length=255, verbose_name=u'Заголовок')
    slug = models.SlugField()
    text = models.TextField(verbose_name=u'Текст')
    creation_date = models.DateTimeField(editable=False, default=datetime.now())

    def __unicode__(self):
        return self.title

    class Meta:
        #app_label = u'Новости'
        verbose_name = u'Новость'
        verbose_name_plural = u'Новости'
