# -*- coding: utf-8 -*-
from django import forms

from .models import PlayListBlock, PlayListItem
from ..models import Video


class PlayListBlockForm(forms.ModelForm):
    class Meta:
        model = PlayListBlock
        fields = ['title', 'limit', 'sort_order']


class PlayListItemForm(forms.ModelForm):
    class Meta:
        model = PlayListItem
        fields = ['video', 'sort_order']


class StreamForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'stream', 'description']

    def __init__(self, *args, **kwargs):
        super(StreamForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
