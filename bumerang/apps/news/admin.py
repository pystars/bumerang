# -*- coding: utf-8 -*-
from django.contrib import admin

from bumerang.apps.news.models import NewsCategory, NewsItem


class NewsCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class NewsItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    change_form_template = 'news/admin/change_form.html'


admin.site.register(NewsCategory, NewsCategoryAdmin)
admin.site.register(NewsItem, NewsItemAdmin)
