# -*- coding: utf-8 -*-
from django import forms

from bumerang.apps.utils.forms import S3StorageFormMixin
from models import Video


class BaseVideoForm(S3StorageFormMixin, forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(BaseVideoForm, self).__init__(*args, **kwargs)
        self.fields['album'].queryset = self.fields['album'].queryset.filter(
            owner=user)
        for name, field in self.fields.items():
            if (field.widget.__class__ == forms.widgets.TextInput
                or field.widget.__class__ == forms.widgets.Textarea):
                if field.widget.attrs.has_key('class'):
                    field.widget.attrs['class'] += ' wide'
                else:
                    field.widget.attrs.update({'class': 'wide'})


class VideoCreateForm(BaseVideoForm):

    class Meta:
        model = Video
        fields = (
            'title',
            'original_file',
            'album',
            'category',
            'description'
        )

    def __init__(self, *args, **kwargs):
        super(VideoCreateForm, self).__init__(*args, **kwargs)
        self.fields['original_file'].required = False


class VideoForm(BaseVideoForm):

    class Meta:
        model = Video
        widgets = {'access': forms.widgets.RadioSelect}
        fields = (
            'title',
            'album',
            'original_file',
            'category',
            'description',
            'year',
            'genre',
            'country',
            'city',
            'authors',
            'teachers',
            'manager',
            'festivals',
        )


class VideoUpdateAlbumForm(forms.Form):
    video_id = forms.CharField()
    album_id = forms.IntegerField(required=False)
