# -*- coding: utf-8 -*-
from datetime import timedelta

from django.forms.models import BaseInlineFormSet
from django.contrib import admin
from django.contrib import messages

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
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        if not obj:
            self.extra = Video.objects.filter(
                is_in_broadcast_lists=True).count()
        return super(
            PlayListItemAdmin, self).get_formset(request, obj=obj, **kwargs)


class PlayListAdmin(admin.ModelAdmin):
    inlines = [PlayListItemAdmin,]

    class Media:
        js = ["j/jquery-1.6.2.min.js", "j/jquery-ui.min.js", "j/admin.js"]

    def save_formset(self, request, form, formset, change):
        formset.save()
        offset = 0
        for item in form.instance.playlistitem_set.all():
            if offset + item.video.duration < 86400000:
                item.offset = offset
                item.save()
                offset += item.video.duration
            else:
                notadded_items_count = form.instance.playlistitem_set.filter(
                    sort_order__gte=item.sort_order).count()
                form.instance.playlistitem_set.filter(
                    sort_order__gte=item.sort_order).delete()
                messages.add_message(request, messages.ERROR,
                    u'последние {0} элементов не были добавлены'.format(
                        notadded_items_count))
                break

        form.instance.rotate_till = form.instance.rotate_from + timedelta(
            milliseconds=offset)
        form.instance.save()


admin.site.register(Channel)
admin.site.register(PlayList, PlayListAdmin)
