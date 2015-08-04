# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django.contrib.sites.models import get_current_site
from django.views.generic.base import TemplateView
from django.db.models.aggregates import Min
from bumerang.apps.news.models import NewsItem

from bumerang.apps.video.models import Video
from bumerang.apps.video.playlists.models import PlayList, Channel
from bumerang.apps.video.playlists.views import PlaylistMixin

SCHEDULE_RANGE = 7


class BumerangIndexView(PlaylistMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):

        ctx = super(BumerangIndexView, self).get_context_data(**kwargs)
        channel = Channel.objects.get(
            slug='main',
            site=get_current_site(self.request)
        )
        today = date.today()

        try:
            playlist = PlayList.objects.filter(
                channel=channel,
                rotate_from_date__lte=today).order_by('-rotate_from_date')[0]
            playlist.rotate_from_date = today
        except (PlayList.DoesNotExist, IndexError):
            playlist = None
        if playlist:
            min_day = 1
        else:
            date_min = PlayList.objects.filter(
                channel=channel,
                rotate_from_date__lte=today + timedelta(days=SCHEDULE_RANGE)
            ).aggregate(date_min=Min('rotate_from_date'))['date_min']
            if date_min:
                min_day = (date_min - today).days
            else:
                min_day = SCHEDULE_RANGE
        next_days = [(today + timedelta(days=i)).timetuple()[0:3]
                     for i in xrange(min_day, SCHEDULE_RANGE)]
        new_movies = Video.objects.filter(
            published_in_archive=True, status=Video.READY)[:5]
        top_viewed = Video.objects.filter(
            published_in_archive=True, status=Video.READY
        ).order_by('-views_count',)[:5]
        last_news = NewsItem.objects.filter(
            category__site=get_current_site(self.request))[:4]
        ctx.update(
            last_news=last_news,
            new_movies=new_movies,
            top_viewed=top_viewed,
            playlist=playlist,
            next_days=next_days,
        )
        return ctx
