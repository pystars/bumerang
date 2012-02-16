# -*- coding: utf-8 -*-
from django.contrib import admin

from bumerang.apps.video.models import Video, VideoCategory, VideoGenre


class VideoAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ['original_file', 'created']
    list_display = ['title', 'category', 'created', 'owner',
                    'published_in_archive', 'is_in_broadcast_lists']
    list_editable = ['published_in_archive', 'is_in_broadcast_lists']


class TitleSlugAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Video, VideoAdmin)
admin.site.register(VideoGenre, TitleSlugAdmin)
admin.site.register(VideoCategory, TitleSlugAdmin)