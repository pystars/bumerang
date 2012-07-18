# -*- coding: utf-8 -*-
from django import forms
from django.forms.fields import FileField


class ManyObjectsForm(forms.Form):
    ids = forms.CharField()


class S3StorageFormMixin(object):

    def save(self, commit=True):
        if commit:
            for field in set(f[0] for f in self.fields.items()
            if isinstance(f[1], FileField)) & set(self.changed_data):
#                getattr(self, field).open()
                self.files[field].open()
        return super(S3StorageFormMixin, self).save(commit)
