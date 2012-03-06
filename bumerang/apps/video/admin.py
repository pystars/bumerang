# -*- coding: utf-8 -*-
import os
import shutil

from django.contrib import admin
from django.contrib.admin.actions import delete_selected as _delete_selected

from bumerang.apps.video.mediainfo import video_duration
from bumerang.apps.video.models import Video, VideoCategory, VideoGenre
from bumerang.apps.video.tasks import MakeScreenShots, ConvertVideoTask


class VideoAdmin(admin.ModelAdmin):
    readonly_fields = ['created', 'slug']
    list_display = ['title', 'category', 'created', 'owner', 'status', 'slug',
                    'published_in_archive', 'is_in_broadcast_lists']
    list_editable = ['published_in_archive', 'is_in_broadcast_lists',  'status']
    actions = ['delete_selected']

    def save_model(self, request, obj, form, change):
        obj.save()
        if 'original_file' in form.changed_data:
            obj.duration = video_duration(obj.original_file.path)
            obj.status = obj.PENDING
            obj.save()
            ConvertVideoTask.delay(obj)
        elif {'hq_file', 'mq_file', 'lq_file'} & set(form.changed_data):
            obj.duration = video_duration(obj.best_quality_file().path)
            obj.status = obj.PENDING
            obj.save()
            MakeScreenShots.delay(obj)

    def delete_selected(self, request, queryset):
        if request.POST.get('post'):
            folders = [os.path.split(video.any_file().path)[0]
                for video in queryset.all()
                if video.any_file()
            ]
        result = _delete_selected(self, request, queryset)
        if request.POST.get('post'):
            for folder in folders:
                shutil.rmtree(folder)
        return result
    delete_selected.short_description = u'Удалить вместе с файлами'


class TitleSlugAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Video, VideoAdmin)
admin.site.register(VideoGenre, TitleSlugAdmin)
admin.site.register(VideoCategory, TitleSlugAdmin)