# -*- coding: utf-8 -*-
from django import forms

from models import PhotoAlbum


class PhotoAlbumForm(forms.ModelForm):
    class Meta:
        model = PhotoAlbum
        fields = ('title', 'description', 'category',)


class PhotoAlbumCoverForm(forms.ModelForm):
    class Meta:
        model = PhotoAlbum
        fields = ('cover',)
