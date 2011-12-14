# -*- coding: utf-8 -*-


import time

from django.shortcuts import render

def upload_view(request):

    if (request.method == 'GET'):
        return render(request, 'video/upload.html')

    if (request.method == 'POST'):

        for x in xrange(1, 100):
            time.sleep(0.1)

        return render(request, 'video/upload.html')