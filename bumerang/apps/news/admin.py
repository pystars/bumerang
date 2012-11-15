# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from tinymce.widgets import TinyMCE

from bumerang.apps.news.models import NewsCategory, NewsItem


class NewsCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class NewsItemForm(forms.ModelForm):
    class Meta:
        model = NewsItem
        widgets = {
            'text': TinyMCE(attrs={'cols': 80, 'rows': 30}),
            'preview_text': TinyMCE(attrs={'cols': 80, 'rows': 30})
        }


class NewsItemAdmin(admin.ModelAdmin):
    form = NewsItemForm
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(NewsCategory, NewsCategoryAdmin)
admin.site.register(NewsItem, NewsItemAdmin)
