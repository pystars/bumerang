# -*- coding: utf-8 -*-
from datetime import timedelta

from django.contrib import admin

from models import PlayList, PlayListItem, Channel


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
        form.instance.rotate_till = form.instance.rotate_from + timedelta(
            milliseconds=offset)
        form.instance.save()


admin.site.register(Channel)
admin.site.register(PlayList, PlayListAdmin)
