# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from bumerang.apps.utils.models import TitleUnicode, nullable
from bumerang.apps.utils.media_storage import media_storage
from bumerang.apps.video.models import Video


def video_album_preview_upload_to(instance, filename):
    return 'previews/video-album/{0}/{1}'.format(instance.owner.slug, filename)


class VideoAlbum(models.Model, TitleUnicode):
    owner = models.ForeignKey(User)
    title = models.CharField(u'Название', max_length=100)
    description = models.TextField(u'Описание', **nullable)
    image = models.ImageField(
        u'Обложка', storage=media_storage,
        upload_to=video_album_preview_upload_to, **nullable)
    cover = models.ForeignKey(Video, on_delete=models.SET_NULL, **nullable)

    class Meta:
        verbose_name = u'Видеоальбом'
        verbose_name_plural = u'Видеоальбомы'

    def preview(self):
        if self.image:
            return self.image
        elif self.cover:
            if self.cover.preview():
                return self.cover.preview().thumbnail
        return None