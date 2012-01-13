# -*- coding: utf-8 -*-
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from django.views.generic.base import TemplateView
from apps.video.models import PlayList, Channel

class BumerangIndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        ctx = super(BumerangIndexView, self).get_context_data(**kwargs)

        main_channel = Channel.objects.get(slug='main')
        try:
            ctx.update({'playlist': PlayList.objects.filter(
                channel=main_channel, rotate_till__gte=datetime.now()).get()})
        except PlayList.DoesNotExist:
            pass #no playlist

        try:
            main_channel = Channel.objects.get(slug='main')
            playlist = PlayList.objects.get(channel=main_channel)
        except ObjectDoesNotExist:
            playlist = False

        ctx.update({
            'playlist': playlist,
        })
        return ctx