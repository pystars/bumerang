# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import json

from django.contrib.sites.models import get_current_site
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.timezone import now, localtime
from django.template.loader import render_to_string
from django.views.generic.dates import (
    DateDetailView, _date_from_string, DateMixin)
from django.views.generic.detail import BaseDetailView

from bumerang.apps.utils.views import GenericFormsetWithFKUpdateView, AjaxView
from bumerang.apps.video.playlists.forms import (
    PlayListBlockForm, PlayListItemForm)
from models import PlayList, PlayListItem, PlayListBlock, Channel


class PlaylistMixin(DateMixin):

    date_field = 'rotate_from_date'
    channel = None
    #
    # def get_playlist_by_date(self, queryset, date):
    #     lookup = {'rotate_from_date__lte': date}
    #     lookup.update(channel__slug=self.get_channel(),
    #                   channel__site=get_current_site(self.request))
    #     last = list(queryset.filter(**lookup).order_by('-rotate_from_date')[:1])
    #     if last:
    #         playlist = last[0]
    #     else:
    #         raise Http404(u'нет плейлиста для указанных даты и канала')
    #     playlist.rotate_from_date = date
    #     return playlist

    def get_playlist_by_date(self, date):
        channel = self.get_channel()
        last = list(channel.playlist_set.filter(
            rotate_from_date__lte=date).order_by('-rotate_from_date')[:1])
        if last:
            playlist = last[0]
            playlist.rotate_from_date = date
            return playlist
        raise Http404(u'нет плейлиста для указанных даты и канала')

    def get_channel(self):
        channel = self.channel
        if channel is None:
            try:
                channel = self.kwargs['channel']
            except KeyError:
                try:
                    channel = self.request.GET['channel']
                except KeyError:
                    raise Http404(_(u"No channel specified"))
        return get_object_or_404(
            Channel, slug=channel, site=get_current_site(self.request))


class PlaylistDetailView(DateDetailView, PlaylistMixin):
    model = PlayList
    allow_future = True
    month_format = '%m'

    def get_object(self, queryset=None):
        super(PlaylistDetailView, self).get_object()
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()
        date = _date_from_string(
            year, self.get_year_format(),
            month, self.get_month_format(),
            day, self.get_day_format())

        # Use a custom queryset if provided
        qs = queryset or self.get_queryset()
        return self.get_playlist_by_date(date)


class JSONCurrentPlaylistItemView(BaseDetailView, PlaylistMixin):
    model = PlayListItem

    def __init__(self, **kwargs):
        super(JSONCurrentPlaylistItemView, self).__init__(**kwargs)
        self.now = localtime(now())
        self.offset = None

    def get_object(self, queryset=None):
        today = datetime.today()
        playlist = self.get_playlist_by_date(today)
        day_offset = (
            self.now.hour * 3600 + self.now.minute * 60 + self.now.second)
        self.offset = (self.now.hour % playlist.duration * 3600 +
                       self.now.minute * 60 + self.now.second)
        skip = 0
        block = None
        blocks = playlist.blocks()
        for block in blocks:
            if skip + block.limit * 60 > self.offset:
                break
            skip += block.limit * 60
        if block is not None:
            # if we found a block which plays now
            qs = list(block.playlistitem_set.filter(
                offset__lte=self.offset * 1000
                ).order_by('-sort_order')[:1])
            if qs:
                item = qs[0]
                item.playlist = playlist
                return item
            try:
                # if here are no items in current block anymore check next block
                block = next(blocks)
                qs = list(block.playlistitem_set.all()[:1])
                if qs:
                    item = qs[0]
                    item.playlist = playlist
                    item.delay = block.offset() * 60 - self.offset
                    return item
            except StopIteration:
                pass
        # if here are no blocks anymore for today
        playlist = self.get_playlist_by_date(today + timedelta(days=1))
        try:
            item = playlist.get_first_item()
            if item:
                item.playlist = playlist
                item.delay = 24 * 60 * 60 - day_offset
                return item
        except PlayListItem.DoesNotExist:
            pass
        raise Http404(u'окончание программы')

    def get_context_data(self, **kwargs):
        playlistitem = self.get_object()
        result = dict(
            id=playlistitem.id,
            comment=playlistitem.video.title,
            movie_description=render_to_string(
                'snippets/video_description.html',
                {'object': playlistitem.video}),
            file=playlistitem.video.rtmp_url()
        )
        if getattr(playlistitem, 'delay', None) is None:
            result['offset'] = int(
                (self.offset - playlistitem.block.offset() * 60
                 ) - playlistitem.offset / 1000)
        return result

    def render_to_response(self, context):
        return HttpResponse(json.dumps(context), mimetype="application/json")

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)


class PlayListBlocksEditView(AjaxView, GenericFormsetWithFKUpdateView):
    model = PlayList
    formset_model = PlayListBlock
    formset_form_class = PlayListBlockForm

    def formset_invalid(self, formset):
        return self.render_to_response(errors=formset.errors)

    def formset_valid(self, formset):
        instances = formset.save(commit=False)
        obj = self.get_object()
        blocks = []
        for instance in instances:
            # the name of fk attribute must be same to lower case of fk model
            setattr(instance, self.model_name, obj)
            instance.save()
            blocks.append(dict(
                id=instance.id,
                title=instance.title,
                sort_order=instance.sort_order,
                limit=instance.limit)
            )
        return self.render_to_response(blocks=blocks)


class PlayListItemsEditView(AjaxView, GenericFormsetWithFKUpdateView):
    model = PlayListBlock
    formset_model = PlayListItem
    formset_form_class = PlayListItemForm

    def formset_invalid(self, formset):
        return self.render_to_response(errors=formset.errors)

    def formset_valid(self, formset):
        instances = formset.save(commit=False)
        obj = self.get_object()
        items = []
        for instance in instances:
            # the name of fk attribute must be same to lower case of fk model
            instance.block = obj
            instance.save()
            items.append({'id': instance.pk})

        offset = 0
        for item in obj.playlistitem_set.values(
                'pk', 'video__duration').select_related('video__duration'):
            PlayListItem.objects.filter(pk=item['pk']).update(offset=offset)
            offset += item['video__duration']

        block = {'duration': offset, 'id': obj.pk}
        return self.render_to_response(items=items, block=block)
