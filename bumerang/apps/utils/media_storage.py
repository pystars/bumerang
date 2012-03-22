# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.conf import settings


if settings.LOCALHOST:
    from storages.backends.overwrite import OverwriteStorage
    media_storage = OverwriteStorage()
else:
    from storages.backends.s3boto import S3BotoStorage
    media_storage = S3BotoStorage(bucket=settings.AWS_MEDIA_STORAGE_BUCKET_NAME)