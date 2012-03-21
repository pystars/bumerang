# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin

from bumerang.apps.utils.views import OwnerMixin, AjaxView
from bumerang.apps.video.models import Video
from forms import VideoAlbumForm, VideoAlbumCoverForm
from models import VideoAlbum


class VideoSetCoverView(AjaxView, OwnerMixin, UpdateView):
    model = VideoAlbum
    form_class = VideoAlbumCoverForm

    def form_valid(self, form):
        cover = form.cleaned_data['cover']
        self.object = form.save(commit=False)
        if (self.object.id == cover.album_id
        and self.object.owner == self.request.user):
            self.object.preview = cover.preview()
            self.object.save()
        return self.render_to_response(result=True)

    def form_invalid(self, form):
        return self.render_to_response(result=False)


class VideoAlbumUpdateView(OwnerMixin, UpdateView):
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
        return reverse('album-video-add',
            kwargs={'video_album_id': self.object.id})


class VideoAlbumDetailView(DetailView):
    model = VideoAlbum

    def get_context_data(self, **kwargs):
        videos = self.object.video_set.all()
        if not self.request.user.id == self.object.owner_id:
            videos = videos.filter(status=Video.READY)
        ctx = super(VideoAlbumDetailView, self).get_context_data(**kwargs)
        ctx['videos'] = videos
        return ctx
