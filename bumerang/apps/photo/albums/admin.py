# -*- coding: utf-8 -*-
from django.contrib import admin

from models import PhotoAlbum, PhotoCategory

class TitleSlugAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(PhotoCategory, TitleSlugAdmin)
admin.site.register(PhotoAlbum)
