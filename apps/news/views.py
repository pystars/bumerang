# -*- coding: utf-8 -*-

from django.views.generic import ListView, DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.views.generic.list_detail import object_list

from apps.news.models import *

class NewsRootView(ListView):
    def get(self, request, *args, **kwargs):
        categories = NewsCategory.objects.all()
        news_list = NewsItem.objects.all().order_by('-creation_date')

        return object_list(request,
                           queryset=news_list,
                           paginate_by=10,
                           extra_context={
                               'news_categories': categories,
                           })


class CategoryView(ListView):
    def get(self, request, slug):
        try:
            categories = NewsCategory.objects.all()
            news_category = NewsCategory.objects.get(slug=slug)
            news_list = news_category.news.all().order_by('-creation_date')
        except ObjectDoesNotExist:
            raise Http404

        return object_list(request,
                           queryset=news_list,
                           template_name="news/news_category.html",
                           paginate_by=10,
                           extra_context={
                               'current_category': news_category,
                               'categories': categories,
                           })



class SingleNewsItemView(DetailView):
    template_name = "news/single_news.html"

    def get(self, request, category_slug, news_slug):
        try:
            self.category = NewsCategory.objects.get(slug=category_slug)
            self.object = self.category.news.get(slug=news_slug)
        except ObjectDoesNotExist:
            raise Http404

        context = self.get_context_data(
            object=self.object,
            category=self.category,
            categories=NewsCategory.objects.all(),
        )
        return self.render_to_response(context)
