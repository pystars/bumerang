# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from apps.utils.models import TitleUnicode, nullable
from apps.photo.models import Photo


class PhotoAlbum(models.Model, TitleUnicode):
    owner = models.ForeignKey(User)
    title = models.CharField(u'Название', max_length=100)
    description = models.TextField(u'Описание')
    cover = models.OneToOneField(Photo, on_delete=models.SET_NULL, **nullable)

    class Meta:
        verbose_name = u'Видеоальбом'
        verbose_name_plural = u'Видеоальбомы'

    def preview(self):
        if self.cover:
            return self.cover
        return None
