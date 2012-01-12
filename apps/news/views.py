# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from apps.news.models import NewsItem, NewsCategory


class NewsContextMixin(object):
    model = NewsItem

    def get_context_data(self, **kwargs):
        ctx = super(NewsContextMixin, self).get_context_data(**kwargs)
        ctx.update({'news_categories': NewsCategory.objects.all(),})
        return ctx


class NewsListView(NewsContextMixin, ListView):
    paginate_by = 10

    def get_queryset(self):
        qs = super(NewsListView, self).get_queryset()
        if 'category' in self.kwargs:
            qs = qs.filter(category__slug=self.kwargs['category'])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(NewsListView, self).get_context_data(**kwargs)
        if 'category' in self.kwargs:
            ctx.update({'current_category': get_object_or_404(
                    NewsCategory, slug=self.kwargs['category'])})
        return ctx


class NewsItemDetailView(NewsContextMixin, DetailView):
    pass
