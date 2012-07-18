# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView

from bumerang.apps.advices.models import Advice


class AdvicesListView(ListView):
    model = Advice
    paginate_by = 10

    def get_queryset(self):
        return super(AdvicesListView, self).get_queryset().filter(level=0)


class AdviceDetailView(DetailView):
    model = Advice
    slug_field = 'url'

    def get_context_data(self, **kwargs):
        ctx = super(AdviceDetailView, self).get_context_data(**kwargs)
        ctx.update(children=self.object.get_children())
        return ctx
