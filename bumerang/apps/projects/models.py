# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models

from bumerang.apps.utils.media_storage import media_storage
from bumerang.apps.utils.models import FileModelMixin, nullable


class Project(FileModelMixin, models.Model):
    title = models.CharField(max_length=255, verbose_name=u'Название')
    text = models.TextField(verbose_name=u'Описание проекта')
    image = models.ImageField(
        u'Изображение', storage=media_storage, upload_to='projects',
        help_text=u'Пропорции изображения - 11x3, минимальная и желательная '
                  u'ширина изображения - 220px. Обязательно соблюдайте эти '
                  u'параметры, иначе верстка на главной странице поплывет',
        **nullable)

    videos = models.ManyToManyField(
        'video.Video', verbose_name=u'Видео проекта')

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Проект'
        verbose_name_plural = u'Проекты'

    def get_absolute_url(self):
        return reverse('project-detail', args=[self.pk])
