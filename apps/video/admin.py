# -*- coding: utf-8 -*-
from django.contrib import admin

from apps.video.models import *


class VideoAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class VideoGenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class VideoCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class PlayListItemAdmin(admin.TabularInline):
    model = PlayListItem
    readonly_fields = ['play_from', 'play_till', 'offset']
    ordering = ['sort_order', 'id']
    extra = 1

class PlayListAdmin(admin.ModelAdmin):

    inlines = [PlayListItemAdmin,]

    def save_formset(self, request, form, formset, change):
        formset.save()
        offset = 0
        for item in form.instance.playlistitem_set.all():
            item.offset = offset
            item.save()
            offset += item.video.duration


admin.site.register(Video, VideoAdmin)
admin.site.register(VideoGenre, VideoGenreAdmin)
admin.site.register(VideoCategory, VideoCategoryAdmin)
admin.site.register(Channel)
admin.site.register(PlayList, PlayListAdmin)
