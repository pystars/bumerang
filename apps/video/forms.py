# -*- coding: utf-8 -*-
from django import forms
from apps.video.models import Video

class VideoForm(forms.ModelForm):
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