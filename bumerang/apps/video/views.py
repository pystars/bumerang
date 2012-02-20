# -*- coding: utf-8 -*-
import json

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q, F
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import ModelFormMixin, UpdateView, BaseFormView
from django.views.generic.list import MultipleObjectMixin

from bumerang.apps.utils.views import AjaxView, OwnerMixin
from albums.models import VideoAlbum
from models import Video
from tasks import ConvertVideoTask
from forms import VideoForm, VideoUpdateAlbumForm, VideoCreateForm
from mediainfo import video_duration


class VideoMoveView(AjaxView, OwnerMixin, BaseFormView, MultipleObjectMixin):
    model = Video
    form_class = VideoUpdateAlbumForm
    
    def get_queryset(self, **kwargs):
        return super(VideoMoveView, self).get_queryset(**kwargs)

    def form_valid(self, form):
        try:
            kwargs = dict(pk=int(form.cleaned_data['video_id']))
        except ValueError:
            try:
                kwargs = dict(id__in=map(int,
                    json.loads(form.cleaned_data['video_id'])))
            except ValueError:
                return HttpResponseForbidden()
        if 'album_id' in form.cleaned_data:
            album = get_object_or_404(VideoAlbum,
                pk=form.cleaned_data['album_id'], owner=self.request.user)
        else:
            album = None
        if self.get_queryset().filter(**kwargs).update(album=album):
            msg = u'Видео успешно перемещено'
        else:
            msg = u'Ошибка перемещения видео'
        return super(VideoMoveView, self).render_to_response(message=msg)


class VideoDetailView(DetailView):
    model = Video

    def get(self, request, **kwargs):
        response = super(VideoDetailView, self).get(request, **kwargs)
        self.get_queryset().update(views_count=F('views_count') + 1)
        return response


class VideoCreateView(CreateView):
    model = Video

    def get_form(self, form_class):
        return VideoCreateForm(self.request.user, **self.get_form_kwargs())

    def get_initial(self):
        result = super(VideoCreateView, self).get_initial()
        result.update(album=self.kwargs.get('video_album_id', None))
        return result

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.duration = video_duration(self.object.original_file.file)
        self.object.save()
        ConvertVideoTask.delay(self.object)
        return super(ModelFormMixin, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.ERROR, u'Ошибка при загрузке видео')
        return super(VideoCreateView, self).form_invalid(form)


class VideoUpdateView(OwnerMixin, UpdateView):
    model = Video

    def get_form(self, form_class):
        return VideoForm(self.request.user, **self.get_form_kwargs())

    def get_success_url(self):
        return reverse('video-edit', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if 'original_file' in form.changed_data:
            self.object.duration = video_duration(
                self.object.original_file.file)
            self.object.status = self.object.PENDING
            self.object.save()
            ConvertVideoTask.delay(self.object)
        else:
            self.object.save()
        messages.add_message(self.request, messages.SUCCESS,
            u'Информация о видео успешно обновлена')
        return super(VideoUpdateView, self).form_valid(form)


class VideoListView(ListView):
    queryset = Video.objects.filter(
        Q(hq_file__isnull=False) |
        Q(mq_file__isnull=False) |
        Q(lq_file__isnull=False),
        published_in_archive=True,
    )
    paginate_by = 5


#def save_upload( uploaded, filename, raw_data ):
#    '''
#    raw_data: if True, uploaded is an HttpRequest object with the file being
#              the raw post data
#              if False, uploaded has been submitted via the basic form
#              submission and is a regular Django UploadedFile in request.FILES
#    '''
#    try:
#        from io import FileIO, BufferedWriter
#
#        with BufferedWriter(FileIO(VIDEO_UPLOAD_PATH + filename, "wb")) as dest:
#            # if the "advanced" upload, read directly from the HTTP request
#            # with the Django 1.3 functionality
#            if raw_data:
#                foo = uploaded.read(1024)
#                while foo:
#                    dest.write(foo)
#                    foo = uploaded.read(1024)
#                    # if not raw, it was a form upload so read in the normal
#                    # Django chunks fashion
#            else:
#                for c in uploaded.chunks():
#                    dest.write(c)
#                # got through saving the upload, report success
#            return True
#    except IOError:
#        # could not open the file most likely
#        pass
#    return False

#def upload_view(request):
#
#    if request.method == 'GET':
#        return render(request, 'video/upload.html')
#
#    if request.method == 'POST':
#
#        if request.is_ajax():
#            upload = request
#            is_raw = True
#            try:
#                filename = request.GET['qqfile']
#            except KeyError:
#                return HttpResponse(status=500)
#        else:
#            is_raw = False
#            if len(request.FILES) == 1:
#                upload = request.FILES.values()[0]
#            else:
#                raise Http404("Bad upload")
#            filename = upload.name
#
#        success = save_upload(upload, filename, is_raw)
#
#        if success:
#            video = Video(original_filename = filename)
#            try:
#                video.save()
#            except Exception, e:
#                print e
#
#            print 'Model created'
#            return HttpResponse(json.dumps({
#                'success': success
#            }))
#        return HttpResponse(json.dumps({'success': success}))
