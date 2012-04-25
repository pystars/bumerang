# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django.views.generic.base import TemplateView
from django.db.models.aggregates import Min
from django.utils import timezone

from bumerang.apps.video.playlists.models import PlayList, Channel


SCHEDULE_RANGE = 7

class BumerangIndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):

        ctx = super(BumerangIndexView, self).get_context_data(**kwargs)
        main_channel = Channel.objects.get(slug='main')
        today = date.today()
        ctx['current_item'] = None
        try:
            playlist = PlayList.objects.filter(
                channel=main_channel,
                rotate_from_date__lte=today).order_by('-rotate_from_date')[0]
            playlist.rotate_from_date = today
        except (PlayList.DoesNotExist, IndexError):
            playlist = None
        if playlist:
            min_day = 1
        else:
            date_min = PlayList.objects.filter(
                channel=main_channel,
                rotate_from_date__lte=today + timedelta(days=SCHEDULE_RANGE)
            ).aggregate(date_min=Min('rotate_from_date'))['date_min']
            if date_min:
                min_day = (date_min - today).days
            else:
                min_day = SCHEDULE_RANGE
        next_days = [(today + timedelta(days=i)).timetuple()[0:3]
                     for i in xrange(min_day, SCHEDULE_RANGE)]
        if playlist:
            now = timezone.now()
            for item in playlist.playlistitem_set.all():
                item.playlist = playlist
                if item.play_from() <= now < item.play_till():
                    ctx['current_item'] = item
                    break
        ctx.update(
            playlist = playlist,
            next_days = next_days,
        )
        return ctx
