# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.sites.models import get_current_site

from bumerang.apps.news.models import NewsItem, NewsCategory


class NewsContextMixin(object):
    model = NewsItem

    def get_context_data(self, **kwargs):
        ctx = super(NewsContextMixin, self).get_context_data(**kwargs)
        ctx.update({'news_categories': NewsCategory.objects.filter(
            site=get_current_site(self.request))})
        return ctx


class NewsListView(NewsContextMixin, ListView):
    paginate_by = 10

    def get_queryset(self):
        qs = super(NewsListView, self).get_queryset()
        if 'category' in self.kwargs:
            qs = qs.filter(category__slug=self.kwargs['category'])
        return qs.filter(category__site=get_current_site(self.request))

    def get_context_data(self, **kwargs):
        ctx = super(NewsListView, self).get_context_data(**kwargs)
        if 'category' in self.kwargs:
            ctx.update({'current_category': get_object_or_404(
                NewsCategory, slug=self.kwargs['category'])})
        return ctx


class NewsItemDetailView(NewsContextMixin, DetailView):
    pass
