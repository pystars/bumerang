# -*- coding: utf-8 -*-
import tempfile

from django.contrib import admin

from ..utils.admin import TitleSlugAdmin
from .converting.mediainfo import video_duration
from .models import Video, VideoCategory, VideoGenre
from .converting.tasks import MakeScreenShots


class VideoAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'get_owner_profile', 'duration',
                       'views_count', 'get_absolute_url')
    list_display = ('title', 'get_absolute_url', 'category',
                    'get_owner_profile', 'owner', 'status', 'created',
                    'published_in_archive', 'is_in_broadcast_lists')
    list_editable = ('category', 'published_in_archive',
                     'is_in_broadcast_lists')
    fieldsets = (
        (None, {'fields': (
            ('published_in_archive', 'is_in_broadcast_lists'),
            'title',
            ('get_owner_profile', 'owner'),
            'category',
            'album',
            'status',
            ('hq_file', 'get_download_original_file')
        ),
                'classes': ('main-fieldset',)
        }),
        ('Info options', {'fields': (
            ('year', 'genre'),
            ('country', 'city'),
            ('authors', 'teachers'),
            ('manager', 'agency'),
            'festivals',
            'description',
            'access',
        )}),
        ('Readonly options', {'fields': (
            'duration',
            'views_count',
        ), 'classes': ('collapse',)})
    )
    fields = (
    )
    # actions = ['delete_selected']

    add_form_template = 'admin/video/video/add_form.html'

    def get_duration(self, field):
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(field.file.read())
        field.file.seek(0)
        duration = video_duration(temp_file.name)
        temp_file.close()
        return duration

    def save_model(self, request, obj, form, change):
        if 'hq_file' in form.changed_data:
            obj.duration = self.get_duration(obj.best_quality_file())
            if obj.duration:
                obj.status = Video.PENDING
                obj.save()
                MakeScreenShots.delay(obj.pk)
            else:
                obj.status = Video.ERROR
                obj.save()

#TODO: repair mass deleting
#    def delete_selected(self, request, queryset):
#        if request.POST.get('post'):
#            folders = [os.path.split(video.any_file().path)[0]
#                for video in queryset.all()
#                if video.any_file()
#            ]
#        result = _delete_selected(self, request, queryset)
#        if request.POST.get('post'):
#            for folder in folders:
#                shutil.rmtree(folder)
#        return result
#    delete_selected.short_description = u'Удалить вместе с файлами'


admin.site.register(Video, VideoAdmin)
admin.site.register(VideoGenre, TitleSlugAdmin)
admin.site.register(VideoCategory, TitleSlugAdmin)