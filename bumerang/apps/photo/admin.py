# -*- coding: utf-8 -*-
from django.contrib import admin

from models import Photo, PhotoCategory, PhotoGenre


class PhotoAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ['original_file', 'created']
    list_display = ['title', 'category', 'created', 'owner',
                    'published_in_archive', 'is_in_broadcast_lists']
    list_editable = ['published_in_archive', 'is_in_broadcast_lists']


class TitleSlugAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Photo, PhotoAdmin)
admin.site.register(PhotoGenre, TitleSlugAdmin)
admin.site.register(PhotoCategory, TitleSlugAdmin)