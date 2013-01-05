# -*- coding: utf-8 -*-
from django.contrib import admin

from models import VideoAlbum


class VideoAlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'last_update', 'created', 'get_owner_profile',
                    'get_absolute_url')


admin.site.register(VideoAlbum, VideoAlbumAdmin)
