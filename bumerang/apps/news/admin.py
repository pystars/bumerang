# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.sites.models import get_current_site
from tinymce.widgets import TinyMCE

from bumerang.apps.news.models import NewsCategory, NewsItem


class NewsCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ['title', 'site']

    def get_queryset(self, request):
        return super(NewsCategoryAdmin, self).get_queryset(request).filter(
            site=get_current_site(request))


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

    def get_queryset(self, request):
        return super(NewsItemAdmin, self).get_queryset(request).filter(
            category__site=get_current_site(request))

    def get_field_queryset(self, db, db_field, request):
        qs = super(NewsItemAdmin, self).get_field_queryset(
            db, db_field, request)
        if db_field.name == 'category' and request:
            return NewsCategory.objects.filter(site=get_current_site(request))
        return qs


admin.site.register(NewsCategory, NewsCategoryAdmin)
admin.site.register(NewsItem, NewsItemAdmin)
