# -*- coding: utf-8 -*-

from django.views.generic import ListView, DetailView

from apps.news.models import *


def news_categories():
    return NewsCategory.objects.all()


class NewsListView(ListView):
    model = NewsItem
    paginate_by = 10

    def get_queryset(self):
        qs = super(NewsListView, self).get_queryset()
        if 'category' in self.kwargs:
            qs = qs.filter(category__slug=self.kwargs['category'])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(NewsListView, self).get_context_data(**kwargs)
        ctx.update({'news_categories': news_categories(),})
        if 'category' in self.kwargs:
            ctx.update({'current_category': NewsCategory.objects.get(
                slug=self.kwargs['category']),})
        return ctx


class NewsItemDetailView(DetailView):
    model = NewsItem

    def get_context_data(self, **kwargs):
        ctx = super(NewsItemDetailView, self).get_context_data(**kwargs)
        ctx.update({'news_categories': news_categories(),})
        return ctx
