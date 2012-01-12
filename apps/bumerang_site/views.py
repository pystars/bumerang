# -*- coding: utf-8 -*-

from django.views.generic import ListView
from django.views.generic.base import TemplateView
from apps.video.models import PlayList, Channel

class BumerangIndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        ctx = super(BumerangIndexView, self).get_context_data(**kwargs)

        main_channel = Channel.objects.get(slug='main')
        playlist = PlayList.objects.get(channel=main_channel)

        ctx.update({
            'playlist': playlist,
        })
        return ctx