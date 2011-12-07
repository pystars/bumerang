# -*- coding: utf-8 -*-

from django.views.generic import ListView

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
