# -*- coding: utf-8 -*-
from django.db.models.deletion import ProtectedError
from django.db.models.fields.files import FileField


nullable = dict(null=True, blank=True)
choices = lambda *x: zip(x,x)

class TitleUnicode(object):
    title = ''
    def __unicode__(self):
        return u'{0}'.format(self.title)


class FileModelMixin(object):

    def delete(self, **kwargs):
        try:
            super(self.__class__, self).delete(**kwargs)
            for field in self._meta.fields:
                if isinstance(field, FileField) and getattr(self, field.name):
                    getattr(self, field.name).delete()
        except ProtectedError:
            pass #TODO: raise delete error, say it to user
