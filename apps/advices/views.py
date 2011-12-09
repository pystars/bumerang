# -*- coding: utf-8 -*-

from django.views.generic import ListView, DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from apps.advices.models import Advice


class AdvicesIndexView(ListView):
    template_name = "advices.html"
    model = Advice

class SingleAdviceView(DetailView):
    template_name = "advice_single.html"

    def get(self, request, url):
        # Strip all trailing slashes
        while (url[-1:] == "/"):
            url = url[0:-1]
        try:
            self.object = Advice.objects.get(url=url)
        except ObjectDoesNotExist:
            raise Http404

        context = self.get_context_data()
        return self.render_to_response(context)