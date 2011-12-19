# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.video.models import *

class VideoAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

class VideoGenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

class VideoCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Video, VideoAdmin)
admin.site.register(VideoGenre, VideoGenreAdmin)
admin.site.register(VideoCategory, VideoCategoryAdmin)
