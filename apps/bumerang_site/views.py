# -*- coding: utf-8 -*-

from django.views.generic import ListView
from django.views.generic.base import TemplateView

class BumerangIndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        ctx = super(BumerangIndexView, self).get_context_data(**kwargs)
        ctx.update({

        })
        return ctx