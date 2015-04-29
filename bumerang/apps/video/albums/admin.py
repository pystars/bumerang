# -*- coding: utf-8 -*-
from django.contrib import admin

from models import VideoAlbum


class VideoAlbumAdmin(admin.ModelAdmin):
    readonly_fields = ('owner',)
    list_display = ('title', 'last_update', 'created', 'owner',
                    'get_absolute_url')


admin.site.register(VideoAlbum, VideoAlbumAdmin)
