# -*- coding: utf-8 -*-
from django.db.models.deletion import ProtectedError
from django.db.models.fields.files import FileField, ImageField


nullable = dict(null=True, blank=True)
choices = lambda *x: zip(x,x)

class TitleUnicode(object):
    title = ''
    def __unicode__(self):
        return u'{0}'.format(self.title)


class FileModelMixin(object):

    def not_empty_file_fields(self):
        return [field for field in self.__class__._meta.fields
                if isinstance(field, (FileField, ImageField))
                and getattr(self, field.name)]

    def delete(self, *args, **kwargs):
        try:
            # super(FileModelMixin, self).delete(*args, **kwargs)
            for field in self.not_empty_file_fields():
                getattr(self, field.name).delete()
            super(FileModelMixin, self).delete(*args, **kwargs)
        except ProtectedError:
            pass #TODO: raise delete error, say it to user
