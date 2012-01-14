# -*- coding: utf-8 -*-
from django import forms
from apps.video.models import Video, VideoAlbum

class VideoForm(forms.ModelForm):
    access = forms.ChoiceField(choices=Video.ACCESS_FLAGS, initial=1)

    class Meta:
        model = Video
        fields = ('title',
                  'slug',
                  'album',
                  'category',
                  'description',
                  'year',
                  'genre',
                  'country',
                  'city',
                  'authors',
                  'teachers',
                  'festivals',
                  'access')

class VideoAlbumForm(forms.ModelForm):
    class Meta:
        model = VideoAlbum
        exclude = ('user',)