# -*- coding: utf-8 -*-
import json
from datetime import timedelta, date

from django.contrib.sites.models import get_current_site
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.views.generic import View, TemplateView
from django.views.generic.dates import (
    DateDetailView, _date_from_string, DateMixin, YearMixin, DayMixin,
    MonthMixin)

from bumerang.apps.utils.views import GenericFormsetWithFKUpdateView, AjaxView
from bumerang.apps.video.playlists.forms import (
    PlayListBlockForm, PlayListItemForm)
from .models import PlayList, PlayListItem, PlayListBlock, Channel
from .utils import Schedule, CurrentItem


class PlaylistMixin(DateMixin):
    date_field = 'rotate_from_date'
    channel = None

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


class ScheduleView(
        YearMixin, MonthMixin, DayMixin, PlaylistMixin, TemplateView):
    model = PlayList
    allow_future = True
    month_format = '%m'
    template_name = 'playlists/playlist_detail.html'

    def get_date(self):
        try:
            year = self.get_year()
            month = self.get_month()
            day = self.get_day()
            return _date_from_string(
                year, self.get_year_format(),
                month, self.get_month_format(),
                day, self.get_day_format())
        except Http404:
            return date.today()

    def get_context_data(self, **kwargs):
        today = date.today()
        schedule = Schedule(self.get_channel(), self.get_date())
        kwargs['seven_days'] = ((today + timedelta(days=i)) for i in range(7))
        kwargs['playlist'] = schedule.playlist
        kwargs['current_date'] = self.get_date()
        kwargs['schedule'] = schedule
        return super(ScheduleView, self).get_context_data(**kwargs)


class JSONCurrentPlaylistItemView(View, PlaylistMixin):
    def get_context_data(self, **kwargs):
        controller = CurrentItem(self.get_channel())
        item = controller.get_current_item()
        result = {
            'countdown': controller.get_countdown(),
        }
        if item:
            result['item'] = {
                'id': item.id,
                'comment': item.video.title,
                'cycle': controller.get_current_cycle(),
                'movie_description': render_to_string(
                    'snippets/video_description.html',
                    {'object': item.video}),
                'file': item.video.rtmp_url(),
                'offset': controller.offset_in_block - item.offset / 1000
            }
        return result

    def get(self, request, *args, **kwargs):
        return HttpResponse(
            json.dumps(self.get_context_data()), mimetype="application/json")


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
