# -*- coding: utf-8 -*-
import os

from django.core.files.storage import FileSystemStorage


class RewritableFilesStorage(FileSystemStorage):
    def save(self, name, content):
        try:
            os.remove(self.path(name))
        except OSError:
            pass
        return super(RewritableFilesStorage, self).save(name, content)
