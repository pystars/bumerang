# -*- coding: utf-8 -*-
from django import forms


class ManyObjectsForm(forms.Form):
    ids = forms.CharField()
