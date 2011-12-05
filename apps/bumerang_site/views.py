# -*- coding: utf-8 -*-

from django.views.generic import ListView

class BumerangIndexView(ListView):
    template_name = "index.html"
    queryset = {}
