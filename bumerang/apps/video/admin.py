# -*- coding: utf-8 -*-
from django.contrib import admin
from bumerang.apps.video.mediainfo import video_duration

from bumerang.apps.video.models import Video, VideoCategory, VideoGenre
from bumerang.apps.video.tasks import MakeScreenShots, ConvertVideoTask


class VideoAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ['original_file', 'created']
    list_display = ['title', 'category', 'created', 'owner',
                    'published_in_archive', 'is_in_broadcast_lists']
    list_editable = ['published_in_archive', 'is_in_broadcast_lists']

    def save_model(self, request, obj, form, change):
        if 'original_file' in form.changed_data:
            obj.duration = video_duration(obj.original_file.file)
            obj.status = obj.PENDING
            obj.save()
            ConvertVideoTask.delay(obj)
        elif {'hq_file', 'mq_file', 'lq_file'} & set(form.changed_data):
            obj.duration = video_duration(obj.best_quality_file().file)
            obj.status = obj.PENDING
            obj.save()
            MakeScreenShots.delay(obj)
        else:
            obj.save()


class TitleSlugAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Video, VideoAdmin)
admin.site.register(VideoGenre, TitleSlugAdmin)
admin.site.register(VideoCategory, TitleSlugAdmin)