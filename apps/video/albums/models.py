# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from apps.utils.models import TitleUnicode, nullable
from apps.video.models import Video


class VideoAlbum(models.Model, TitleUnicode):
    owner = models.ForeignKey(User)
    title = models.CharField(u'Название', max_length=100)
    description = models.TextField(u'Описание', **nullable)
    cover = models.OneToOneField(Video, on_delete=models.SET_NULL, **nullable)

    class Meta:
        verbose_name = u'Видеоальбом'
        verbose_name_plural = u'Видеоальбомы'

    def preview(self):
        if self.cover:
            return self.cover.preview
        return None
