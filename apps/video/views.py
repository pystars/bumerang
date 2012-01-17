# -*- coding: utf-8 -*-
import json

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import Http404
from django.db.models import Q
from django.views.generic import ListView, View, CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.edit import ModelFormMixin, UpdateView
from apps.video.forms import VideoAlbumCoverForm

from settings import VIDEO_UPLOAD_PATH
from models import Video, VideoAlbum
from forms import (VideoForm, VideoAlbumForm, VideoCreateForm,
                   AlbumVideoCreateForm)


class VideosDeleteView(View):
    def get_queryset(self):
        ids = json.loads(self.request.POST['ids'])
        # Если владелец - текущий пользователь, выбирутся
        # все видео. Иначе ни одного, удалять будет нечего.
        # И пусть хацкеры ломают головы ;)
        return Video.objects.filter(id__in=ids, owner=self.request.user)

    def get(self, request, **kwargs):
        return HttpResponse(status=403)

    def post(self, request, **kwargs):
        videos = self.get_queryset()
        if videos.count() > 1:
            msg = u'Видео успешно удалены'
        else:
            msg = u'Видео успешно удалено'
        for video in videos.all():
            video.delete()
        return HttpResponse(json.dumps({'message': msg}),
            mimetype="application/json")


class VideoalbumsDeleteView(View):
    def get_queryset(self):
        ids = json.loads(self.request.POST['ids'])
        return Video.objects.filter(id__in=ids, owner=self.request.user)

    def get(self, request, **kwargs):
        return HttpResponse(status=403)

    def post(self, request, **kwargs):
        videoalbums = self.get_queryset()
        if videoalbums.count() > 1:
            msg = u'Видеоальбомы успешно удалены'
        else:
            msg = u'Видеоальбом успешно удален'
        for videoalbum in videoalbums.all():
            videoalbum.delete()

        return HttpResponse(json.dumps({'message': msg}),
                            mimetype="application/json")

class VideoMoveView(View):
    model = Video

    def get(self, request, **kwargs):
        return HttpResponse(status=403)

    def post(self, request, **kwargs):
        album = get_object_or_404(VideoAlbum,
            id=request.POST.get('album_id'), owner=request.user)
        if Video.objects.filter(id=request.POST.get('video_id'),
                owner=request.user).update(album=album):
            msg = u'Видео успешно перемещено'
        else:
            msg = u'Ошибка перемещения видео'

        return HttpResponse(json.dumps({'message': msg}),
            mimetype="application/json")


class VideoSetCoverView(UpdateView):
    model = VideoAlbum
    form_class = VideoAlbumCoverForm

    def get_form(self, form_class):
        a = VideoAlbumCoverForm(**self.get_form_kwargs())
        return a

    def get(self, request, **kwargs):
        return HttpResponse(status=403)

    def get_success_url(self):
        messages.add_message(
            self.request, messages.SUCCESS, u'Обложка видеоальбома обновлена')
        return reverse('video-album-detail', args=[self.object.id])

class VideoDeleteView(DeleteView):
    model = Video

    def get_queryset(self):
        return Video.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return self.request.path


class VideoCreateView(CreateView):
    model = Video

    def get_form(self, form_class):
        if self.album():
            return AlbumVideoCreateForm(**self.get_form_kwargs())
        return VideoCreateForm(self.request.user, **self.get_form_kwargs())

    def album(self):
        if 'video_album_id' in self.kwargs:
            try:
                return VideoAlbum.objects.get(
                    owner=self.request.user, pk=self.kwargs['video_album_id'])
            except VideoAlbum.DoesNotExist:
                pass
        return None

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.album():
            self.object.album = self.album()
        self.object.owner = self.request.user
        self.object.save()
        return super(ModelFormMixin, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.ERROR, u'Ошибка при загрузке видео')
        return super(VideoCreateView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super(VideoCreateView, self).get_context_data(**kwargs)
        ctx.update({'video_album': self.album()})
        return ctx


class VideoUpdateView(UpdateView):
    model = Video

    def get_form(self, form_class):
        return VideoForm(self.request.user, **self.get_form_kwargs())

    def get_object(self, queryset=None):
        return Video.objects.get(id=self.kwargs['pk'], owner=self.request.user)

    def get_success_url(self):
        return reverse('video-edit', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        self.object = form.save()
        messages.add_message(self.request, messages.SUCCESS,
            u'Информация о видео успешно обновлена')
        return super(VideoUpdateView, self).form_valid(form)


class VideoListView(ListView):
    queryset = Video.objects.filter(
        Q(hq_file__isnull=False) |
        Q(mq_file__isnull=False) |
        Q(lq_file__isnull=False)
    )
    paginate_by = 25


class XMLDetailView(DetailView):
    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'text/xml'
        return super(XMLDetailView, self).render_to_response(context,
            **response_kwargs)


class VideoAlbumUpdateView(UpdateView):
    model = VideoAlbum
    form_class = VideoAlbumForm

    def get_success_url(self):
        return reverse('video-album-detail', kwargs={'pk': self.object.id})


class VideoAlbumCreateView(CreateView):
    model = VideoAlbum
    form_class = VideoAlbumForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return super(ModelFormMixin, self).form_valid(form)

    def get_success_url(self):
        return reverse('album-video-add', kwargs={'video_album_id': self.object.id})


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
                    # if not raw, it was a form upload so read in the normal
                    # Django chunks fashion
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
        return HttpResponse(json.dumps({'success': success}))
