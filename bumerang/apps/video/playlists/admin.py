# -*- coding: utf-8 -*-
from datetime import timedelta

from django.forms.models import BaseInlineFormSet
from django.contrib import admin

from models import PlayList, PlayListItem, Channel
from bumerang.apps.video.models import Video


class PlayListItemFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        if not kwargs['instance'].pk:
            kwargs['initial'] = [{'video': video}
                for video in Video.objects.filter(is_in_broadcast_lists=True)]
        super(PlayListItemFormSet, self).__init__(*args, **kwargs)


class PlayListItemAdmin(admin.TabularInline):
    model = PlayListItem
    formset = PlayListItemFormSet
    readonly_fields = ['play_from', 'play_till', 'offset']
    ordering = ['sort_order', 'id']


    def __init__(self, parent_model, admin_site):
        super(PlayListItemAdmin, self).__init__(parent_model, admin_site)
        self.extra = Video.objects.filter(is_in_broadcast_lists=True).count()


class PlayListAdmin(admin.ModelAdmin):
    inlines = [PlayListItemAdmin,]

    class Media:
        js = ["j/jquery-1.7.1.min.js", "j/jquery-ui.min.js", "j/admin.js"]

    def save_formset(self, request, form, formset, change):
        formset.save()
        offset = 0
        for item in form.instance.playlistitem_set.all():
            item.offset = offset
            item.save()
            offset += item.video.duration
        form.instance.rotate_till = form.instance.rotate_from + timedelta(
            milliseconds=offset)
        form.instance.save()


admin.site.register(Channel)
admin.site.register(PlayList, PlayListAdmin)
