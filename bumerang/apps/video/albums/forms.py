# -*- coding: utf-8 -*-
from django import forms

from models import VideoAlbum


class VideoAlbumForm(forms.ModelForm):
    class Meta:
        model = VideoAlbum
        fields = ('title', 'description')


class VideoAlbumCoverForm(forms.ModelForm):
    class Meta:
        model = VideoAlbum
        fields = ('cover',)
