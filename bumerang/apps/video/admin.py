# -*- coding: utf-8 -*-
import tempfile

from django.contrib import admin

from ..utils.admin import TitleSlugAdmin
from .converting.mediainfo import video_duration
from .models import Video, VideoCategory, VideoGenre, Preview
from .forms import PreviewForm
from .converting.tasks import MakeScreenShots


class PreviewInline(admin.TabularInline):
    model = Preview
    extra = 1
    form = PreviewForm


class VideoAdmin(admin.ModelAdmin):
    inlines = [PreviewInline]
    readonly_fields = ('created', 'duration', 'views_count', 'get_absolute_url',
                       'get_download_original_file', 'owner_email')
    list_display = ('title', 'get_absolute_url', 'category', 'owner', 'status',
                    'created', 'published_in_archive', 'is_in_broadcast_lists',
                    'owner_email')
    list_editable = ('category', 'published_in_archive',
                     'is_in_broadcast_lists')

    search_fields = ('title',)

    list_filter = ('published_in_archive', 'is_in_broadcast_lists', 'status')

    fieldsets = (
        (None, {'fields': (
            ('published_in_archive', 'is_in_broadcast_lists'),
            'title',
            'owner',
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

    def get_queryset(self, request):
        return super(VideoAdmin, self).get_queryset(request).select_related(
            'owner__email', 'owner__title', 'owner__username')

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

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('owner',)
        return self.readonly_fields

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
