# -*- coding: utf-8 -*-
# from datetime import timedelta

from django.contrib.sites.models import get_current_site
from django import forms
from django.core.urlresolvers import reverse
# from django.forms.models import BaseInlineFormSet
from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib.admin.widgets import AdminDateWidget

from .forms import StreamForm
from .models import PlayList, PlayListItem, Channel, PlayListBlock
from ..models import VideoCategory


# class PlayListItemFormSet(BaseInlineFormSet):
#     def __init__(self, *args, **kwargs):
#         if not kwargs['instance'].pk:
#             kwargs['initial'] = [{'video': video}
#                 for video in Video.objects.filter(is_in_broadcast_lists=True)]
#         super(PlayListItemFormSet, self).__init__(*args, **kwargs)
#
#
# class PlayListItemAdmin(admin.TabularInline):
#     model = PlayListItem
#     formset = PlayListItemFormSet
#     readonly_fields = ['play_from', 'play_till', 'offset']
#     ordering = ['sort_order', 'id']
#     extra = 0
#
#     def get_formset(self, request, obj=None, **kwargs):
#         if not obj:
#             self.extra = Video.objects.filter(
#                 is_in_broadcast_lists=True).count()
#         return super(
#             PlayListItemAdmin, self).get_formset(request, obj=obj, **kwargs)

class PlayListCopyForm(forms.ModelForm):
    _selected_action = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = PlayList
        fields = ['rotate_from_date']
        widgets = {
            'rotate_from_date': AdminDateWidget(),
        }


class PlayListAdmin(admin.ModelAdmin):
    # inlines = [PlayListItemAdmin]

    actions = ['copy_playlist']

    # class Media:
    #     js = ["j/jquery-1.6.2.min.js", "j/jquery-ui.min.js", "j/admin.js"]

    # def save_formset(self, request, form, formset, change):
    #     formset.save()
    #     offset = 0
    #     for item in form.instance.playlistitem_set.all():
    #         if offset + item.video.duration < 86400000:
    #             item.offset = offset
    #             item.save()
    #             offset += item.video.duration
    #         else:
    #             notadded_items_count = form.instance.playlistitem_set.filter(
    #                 sort_order__gte=item.sort_order).count()
    #             form.instance.playlistitem_set.filter(
    #                 sort_order__gte=item.sort_order).delete()
    #             messages.add_message(request, messages.ERROR,
    #                 u'последние {0} элементов не были добавлены'.format(
    #                     notadded_items_count))
    #             break
    #
    #     form.instance.rotate_till = form.instance.rotate_from + timedelta(
    #         milliseconds=offset)
    #     form.instance.save()

    def get_queryset(self, request):
        return super(PlayListAdmin, self).get_queryset(request).filter(
            channel__site=get_current_site(request))

    def copy_playlist(self, request, queryset):

        redirect_response = HttpResponseRedirect(
                    reverse('admin:playlists_playlist_changelist'))
        try:
            playlist = queryset.get()
        except PlayList.MultipleObjectsReturned:
            self.message_user(
                request, u"Можно копировать только один плейлист",
                messages.ERROR)
            return redirect_response
        except PlayList.DoesNotExist:
            self.message_user(
                request, u"Выберите плейлист для копирования", messages.ERROR)
            return redirect_response

        form = None
        if request.POST:
            form = PlayListCopyForm(request.POST)

            if form.is_valid():
                old_playlist = PlayList.objects.get(
                    pk=form.cleaned_data['_selected_action'])
                new_playlist = form.save(commit=False)
                new_playlist.channel = old_playlist.channel
                new_playlist.duration = old_playlist.duration
                new_playlist.save()
                new_block_items = []
                for old_block in old_playlist.playlistblock_set.all():
                    new_block = PlayListBlock.objects.create(
                        playlist=new_playlist, title=old_block.title,
                        sort_order=old_block.sort_order, limit=old_block.limit)
                    for item in old_block.playlistitem_set.all():
                        new_block_items.append(
                            PlayListItem(
                                block=new_block,
                                video=item.video,
                                offset=item.offset,
                                sort_order=item.sort_order)
                        )
                PlayListItem.objects.bulk_create(new_block_items)

                self.message_user(
                    request, u"Плейлист успешно скопирован")
                return redirect_response

        if not form:
            form = PlayListCopyForm(
                initial={'_selected_action': request.POST.getlist(
                    admin.ACTION_CHECKBOX_NAME)})

        opts = self.model._meta

        return TemplateResponse(
            request,
            "admin/playlists/playlist/copy_form.html",
            {'playlist': playlist,
             'adminform': form,
             'app_label': opts.app_label,
             'media': self.media,
             'opts': opts},
            current_app=self.admin_site.name)
    copy_playlist.short_description = u'Скопировать выделенный список'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(
            video_categories=VideoCategory.objects.all(),
            stream_form=StreamForm(),
            # playlists_videos=Video.objects.filter(is_in_broadcast_lists=True)
        )
        return super(PlayListAdmin, self).change_view(
            request, object_id, form_url, extra_context)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'channel':
            kwargs['queryset'] = Channel.objects.filter(
                site=get_current_site(request))
        return super(PlayListAdmin, self).formfield_for_foreignkey(
            db_field, request=None, **kwargs)


class ChannelAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']

    def get_queryset(self, request):
        return super(ChannelAdmin, self).get_queryset(request).filter(
            site=get_current_site(request))


admin.site.register(Channel, ChannelAdmin)
admin.site.register(PlayList, PlayListAdmin)
