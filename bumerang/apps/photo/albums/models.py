# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from bumerang.apps.utils.models import TitleUnicode, nullable
from bumerang.apps.photo.models import Photo


class PhotoAlbum(models.Model, TitleUnicode):
    owner = models.ForeignKey(User)
    title = models.CharField(u'Название', max_length=100)
    description = models.TextField(u'Описание', **nullable)
    cover = models.OneToOneField(Photo, on_delete=models.SET_NULL, **nullable)

    class Meta:
        verbose_name = u'Фотоальбом'
        verbose_name_plural = u'Фотоальбомы'

    def preview(self):
        if self.cover:
            return self.cover
        return None
