# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.news.models import *

class NewsItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

    class Media:
        js = [
            'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
            'j/tinymce_setup.js',
        ]
    
admin.site.register(NewsItem, NewsItemAdmin)
