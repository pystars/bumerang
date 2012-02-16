# -*- coding: utf-8 -*-
from datetime import datetime

from django.views.generic.base import TemplateView

from bumerang.apps.video.playlists.models import PlayList, Channel


class BumerangIndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        ctx = super(BumerangIndexView, self).get_context_data(**kwargs)
        main_channel = Channel.objects.get(slug='main')
        try:
            playlist = PlayList.objects.filter(
                channel=main_channel, rotate_till__gte=datetime.now())[0]
        except PlayList.DoesNotExist:
            playlist = None
        except IndexError:
            playlist = None
        ctx.update({'playlist': playlist})
        return ctx
