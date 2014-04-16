# -*- coding: utf-8 -*-
import datetime

from django.utils import simplejson
from django.http import Http404, HttpResponse
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.views.generic.dates import (DateDetailView, _date_from_string,
                                        DateMixin)
from django.views.generic.detail import BaseDetailView

from models import PlayList, PlayListItem


class PlaylistMixin(DateMixin):

    date_field = 'rotate_from_date'
    channel = None

    def get_playlist_by_date(self, queryset, date):
        date_field = self.get_date_field()
        field = queryset.model._meta.get_field(date_field)
        lookup = {'%s__lte' % field.name: date}
        lookup.update(channel__slug=self.get_channel())
        queryset = queryset.filter(**lookup).order_by('-{0}'.format(date_field))
        try:
            playlist = queryset[0]
        except IndexError:
            raise Http404(u'нет плейлиста для указанных даты и канала')
        playlist.rotate_from_date = date
        return playlist

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
        return channel


class PlaylistDetailView(DateDetailView, PlaylistMixin):
    model = PlayList
    allow_future = True
    month_format = '%m'

    def get_object(self, queryset=None):
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()
        date = _date_from_string(year, self.get_year_format(),
            month, self.get_month_format(),
            day, self.get_day_format())

        # Use a custom queryset if provided
        qs = queryset or self.get_queryset()

        if not self.get_allow_future() and date > datetime.date.today():
            raise Http404(_(u"""Future %(verbose_name_plural)s not available
             because %(class_name)s.allow_future is False.""") % {
                'verbose_name_plural': qs.model._meta.verbose_name_plural,
                'class_name': self.__class__.__name__,
                })

        return self.get_playlist_by_date(qs, date)


class JSONCurrentPlaylistItemView(BaseDetailView, PlaylistMixin):
    model = PlayListItem

    def get_object(self, queryset=None):
        playlist = self.get_playlist_by_date(PlayList.objects,
            datetime.datetime.today())
        try:
            playlistitem = playlist.playlistitem_set.filter(
                offset__lte = (now() - playlist.rotate_from).seconds * 1000
                ).order_by('-sort_order', '-id')[0]
        except self.model.DoesNotExist:
            raise Http404(u'окончание программы')
        playlistitem.playlist = playlist
        return playlistitem


    def get_context_data(self, **kwargs):
        playlistitem = self.get_object()
        return dict(
            id = playlistitem.id,
            comment = playlistitem.video.title,
            movie_description = render_to_string(
                'snippets/video_description.html',
                {'object': playlistitem.video}),
            file = playlistitem.video.rtmp_url(),
            offset = (now() - playlistitem.play_from()).seconds
        )

    def render_to_response(self, context):
        return HttpResponse(
            simplejson.dumps(context), mimetype="application/json")

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)
