# -*- coding: utf-8 -*-
from django import forms
from django.forms.widgets import Textarea, TextInput

from bumerang.apps.utils.forms import S3StorageFormMixin
from .models import Video


class BaseVideoForm(S3StorageFormMixin, forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(BaseVideoForm, self).__init__(*args, **kwargs)
        self.fields['album'].queryset = user.videoalbum_set.all()
        for name, field in self.fields.items():
            if field.widget.__class__ in (Textarea, TextInput):
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' wide'
                else:
                    field.widget.attrs.update({'class': 'wide'})


class VideoCreateForm(BaseVideoForm):

    class Meta:
        model = Video
        fields = (
            'title',
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
            # 'original_file',
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


class GetS3UploadURLForm(forms.Form):
    content_type = forms.CharField()
    filename = forms.CharField()


class PreviewForm(forms.ModelForm):
    class Meta:
        fields = ['image']

    def save(self, commit=True):
        instance = super(PreviewForm, self).save(commit=False)
        if 'image' in self.changed_data:
            instance.set_thumbnails(self.cleaned_data['image'])
        if commit:
            instance.save()
        return instance
