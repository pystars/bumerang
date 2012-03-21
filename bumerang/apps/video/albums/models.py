# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from storages.backends.s3boto import S3BotoStorage

from bumerang.apps.utils.models import TitleUnicode, nullable
from bumerang.apps.video.models import Video

s3storage = S3BotoStorage(bucket=settings.AWS_MEDIA_STORAGE_BUCKET_NAME)


def video_album_preview_upload_to(instance, filename):
    return 'previews/video-album/{0}/{1}'.format(instance.owner.slug, filename)


class VideoAlbum(models.Model, TitleUnicode):
    owner = models.ForeignKey(User)
    title = models.CharField(u'Название', max_length=100)
    description = models.TextField(u'Описание', **nullable)
    preview = models.ImageField(u'Обложка', storage=s3storage,
        upload_to=video_album_preview_upload_to, **nullable)
    cover = models.ForeignKey(Video, on_delete=models.SET_NULL, **nullable)

    class Meta:
        verbose_name = u'Видеоальбом'
        verbose_name_plural = u'Видеоальбомы'
