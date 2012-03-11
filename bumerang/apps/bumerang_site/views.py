# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django.views.generic.base import TemplateView

from bumerang.apps.video.playlists.models import PlayList, Channel


class BumerangIndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        ctx = super(BumerangIndexView, self).get_context_data(**kwargs)
        main_channel = Channel.objects.get(slug='main')
        today = date.today()
        try:
            playlist = PlayList.objects.filter(
                channel=main_channel, rotate_from_date__lte=today)[0]
            playlist.rotate_from_date = today
        except (PlayList.DoesNotExist, IndexError):
            playlist = None
        m_d = lambda x: (x.month, x.day)
        next_days = [m_d(today + timedelta(days=i)) for i in xrange(1, 7)]
        ctx.update({'playlist': playlist, 'next_days': next_days})
        return ctx
