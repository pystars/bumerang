# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, RequestContext

from apps.advices.models import Advice

def show_advices(request):
    return render_to_response("advices.html",
    {
        'advices': Advice.objects.all()
        },
    context_instance=RequestContext(request))


def show_advices_from_url(request, url):
    # Strip all trailing slashes
    while (url[-1:] == "/"):
        url = url[0:-1]

    node = Advice.objects.get(url=url)

    return render_to_response("advice_single.html", {
        'current_node': node,
    },context_instance=RequestContext(request))