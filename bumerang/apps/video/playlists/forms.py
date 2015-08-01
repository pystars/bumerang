# -*- coding: utf-8 -*-
from django import forms

from models import PlayListBlock, PlayListItem


class PlayListBlockForm(forms.ModelForm):
    class Meta:
        model = PlayListBlock
        fields = ['title', 'limit', 'sort_order']


class PlayListItemForm(forms.ModelForm):
    class Meta:
        model = PlayListItem
        fields = ['video', 'sort_order']
