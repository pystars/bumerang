# -*- coding: utf-8 -*-

from django.views.generic import ListView, DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from apps.news.models import *

class NewsRootView(ListView):
    template_name = "news.html"
    object_list = NewsItem.objects.all().order_by('-creation_date')
    categories = NewsCategory.objects.all()

    paginate_by = 10

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(
            object_list=self.object_list,
            news_categories=self.categories,
        )
        return self.render_to_response(context)


class CategoryView(ListView):
    template_name = "news_category.html"

    def get(self, request, slug):
        try:
            self.category = NewsCategory.objects.get(slug=slug)
            self.object_list = self.category.news.all().order_by('-creation_date')
        except ObjectDoesNotExist:
            raise Http404

        context = self.get_context_data(
            object_list=self.object_list,
            category=self.category,
        )
        return self.render_to_response(context)

class SingleNewsItemView(DetailView):
    template_name = "single_news.html"

    def get(self, request, category_slug, news_slug):
        try:
            self.category = NewsCategory.objects.get(slug=category_slug)
            self.object = self.category.news.get(slug=news_slug)
        except ObjectDoesNotExist:
            raise Http404

        context = self.get_context_data(
            object=self.object,
            category=self.category,
        )
        return self.render_to_response(context)
