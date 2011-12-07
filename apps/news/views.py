# -*- coding: utf-8 -*-

from django.views.generic import ListView

from apps.news.models import *

class NewsRootView(ListView):
    template_name = "news.html"
    object_list = NewsItem.objects.all()
    categories = NewsCategory.objects.all()

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(
            object_list=self.object_list,
            news_categories=self.categories,
        )
        return self.render_to_response(context)
