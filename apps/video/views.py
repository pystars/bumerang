# -*- coding: utf-8 -*-
import json

from django.shortcuts import render, HttpResponse
from django.http import Http404
from django.views.generic import ListView, DetailView
from django.db.models import Q

from settings import VIDEO_UPLOAD_PATH
from models import Video


class VideoListView(ListView):
    queryset = Video.objects.filter(
        Q(hq_file__isnull=False) |
        Q(mq_file__isnull=False) |
        Q(lq_file__isnull=False)
    )
    paginate_by = 2

class VideoDetailView(DetailView):
    model = Video


def save_upload( uploaded, filename, raw_data ):
    '''
    raw_data: if True, uploaded is an HttpRequest object with the file being
              the raw post data
              if False, uploaded has been submitted via the basic form
              submission and is a regular Django UploadedFile in request.FILES
    '''
    try:
        from io import FileIO, BufferedWriter

        with BufferedWriter(FileIO(VIDEO_UPLOAD_PATH + filename, "wb")) as dest:
            # if the "advanced" upload, read directly from the HTTP request
            # with the Django 1.3 functionality
            if raw_data:
                foo = uploaded.read(1024)
                while foo:
                    dest.write(foo)
                    foo = uploaded.read(1024)
                    # if not raw, it was a form upload so read in the normal Django chunks fashion
            else:
                for c in uploaded.chunks():
                    dest.write(c)
                # got through saving the upload, report success
            return True
    except IOError:
        # could not open the file most likely
        pass
    return False

def upload_view(request):

    if request.method == 'GET':
        return render(request, 'video/upload.html')

    if request.method == 'POST':

        if request.is_ajax():
            upload = request
            is_raw = True
            try:
                filename = request.GET['qqfile']
            except KeyError:
                return HttpResponse(status=500)
        else:
            is_raw = False
            if len(request.FILES) == 1:
                upload = request.FILES.values()[0]
            else:
                raise Http404("Bad upload")
            filename = upload.name

        success = save_upload(upload, filename, is_raw)

        if success:
            video = Video(original_filename = filename)
            try:
                video.save()
            except Exception, e:
                print e

            print 'Model created'
            return HttpResponse(json.dumps({
                'success': success
            }))
        else:
            return HttpResponse(json.dumps({
                'success': success
            }))

        #return render(request, 'video/valums.html')