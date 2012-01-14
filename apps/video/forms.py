# -*- coding: utf-8 -*-
from django import forms

from apps.video.models import Video, VideoAlbum


class VideoCreateForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = (
            'title',
            'album',
            'original_file',
            'hq_file',
            'mq_file',
            'lq_file',
            'preview',
            'category',
            'description'
        )


class AlbumVideoCreateForm(VideoCreateForm):
    class Meta(VideoCreateForm.Meta):
        exclude = ('album',)


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        widgets = {'access': forms.widgets.RadioSelect}
        fields = (
            'title',
#            'slug',
            'album',
            'original_file',
            'hq_file',
            'mq_file',
            'lq_file',
            'preview',
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


class VideoAlbumForm(forms.ModelForm):
    class Meta:
        model = VideoAlbum
        exclude = ('owner',)