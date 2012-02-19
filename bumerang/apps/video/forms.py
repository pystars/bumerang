# -*- coding: utf-8 -*-
from django import forms

from models import Video


class BaseVideoForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(BaseVideoForm, self).__init__(*args, **kwargs)
        self.fields['album'].queryset = self.fields[
                'album'].queryset.filter(owner=user)

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
            'festivals',
            'access'
        )


class VideoUpdateAlbumForm(forms.Form):
    video_id = forms.CharField()
    album_id = forms.IntegerField()
