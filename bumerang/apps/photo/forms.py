# -*- coding: utf-8 -*-
from django import forms

from bumerang.apps.utils.forms import S3StorageFormMixin
from models import Photo


class BasePhotoForm(S3StorageFormMixin, forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(BasePhotoForm, self).__init__(*args, **kwargs)
        if 'album' in self.fields:
            self.fields['album'].queryset = self.fields[
                'album'].queryset.filter(owner=user)


class PhotoCreateForm(BasePhotoForm):
#    original_file = forms.ImageField(label=u"Оригинальное фото")

    class Meta:
        model = Photo
        fields = (
            'title',
            'original_file',
            'album',
            'description'
        )

    def __init__(self, user, *args, **kwargs):
        super(PhotoCreateForm, self).__init__(user, *args, **kwargs)
        self.fields['album'].queryset = self.fields['album'].queryset.filter(
            owner=user)


class AlbumPhotoCreateForm(BasePhotoForm):

    class Meta:
        model = Photo
        fields = (
            'title',
            'original_file',
            'description'
        )


class PhotoForm(BasePhotoForm):

    class Meta:
        model = Photo
        widgets = {'access': forms.widgets.RadioSelect}
        fields = (
            'title',
            'album',
            'original_file',
            'description',
            'year',
            'genre',
            'country',
            'city',
            'authors',
            'teachers',
            'festivals',
#            'access'
        )


class PhotoUpdateAlbumForm(forms.Form):
    photo_id = forms.CharField()
    album_id = forms.IntegerField()
