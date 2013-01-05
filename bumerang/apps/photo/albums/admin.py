# -*- coding: utf-8 -*-
from django.contrib import admin

from models import PhotoAlbum, PhotoCategory
from bumerang.apps.utils.admin import TitleSlugAdmin


class PhotoAlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'last_update', 'created', 'get_owner_profile',
                    'get_absolute_url')


admin.site.register(PhotoCategory, TitleSlugAdmin)
admin.site.register(PhotoAlbum, PhotoAlbumAdmin)
