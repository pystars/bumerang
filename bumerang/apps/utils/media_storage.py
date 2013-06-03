# -*- coding: utf-8 -*-
"""
make sure you have this setting
AWS_PRELOAD_METADATA = True
and that you have python-dateutils==1.5 installed
"""
from __future__ import absolute_import
from datetime import datetime

from dateutil import tz
from django.conf import settings
from storages.backends.s3boto import S3BotoStorage
from storages.backends.overwrite import OverwriteStorage
from filebrowser.storage import S3BotoStorageMixin, FileSystemStorageMixin


class CachedS3BotoStorage(S3BotoStorage, S3BotoStorageMixin):
    """
    S3 storage backend that saves the files locally, too.
    """
#    def __init__(self, *args, **kwargs):
#        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
#        self.local_storage = get_storage_class(
#            "compressor.storage.CompressorFileStorage")()
#
#    def save(self, name, content):
#        name = super(CachedS3BotoStorage, self).save(name, content)
#        self.local_storage._save(name, content)
#        return name

    def modified_time(self, path):
        try:
            return super(CachedS3BotoStorage, self).modified_time(path)
        except AttributeError:
            return datetime.now().astimezone(
                tz.gettz(settings.TIME_ZONE)).replace(tzinfo=None)

    def isdir(self, name):
        if not name: # Empty name is a directory
            return True
        name = self._encode_name(self._normalize_name(self._clean_name(name)))
        return bool(self.bucket.get_all_keys(max_keys=1, prefix=name + '/'))

    def makedirs(self, name):
        name = self._encode_name(name)
        if not name.endswith('/'):
            name += '/'
        key = self.bucket.new_key(name)
        key.set_contents_from_string('', reduced_redundancy=True)


class LocalStorage(OverwriteStorage, FileSystemStorageMixin):
    pass


if settings.LOCALHOST:
    media_storage = LocalStorage()
else:
    media_storage = CachedS3BotoStorage(
        bucket=settings.AWS_MEDIA_STORAGE_BUCKET_NAME,
        custom_domain=settings.AWS_S3_MEDIA_CUSTOM_DOMAIN
    )
