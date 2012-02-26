# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin

from bumerang.apps.utils.views import OwnerMixin, AjaxView
from forms import VideoAlbumForm, VideoAlbumCoverForm
from models import VideoAlbum


class VideoSetCoverView(AjaxView, OwnerMixin, UpdateView):
    model = VideoAlbum
    form_class = VideoAlbumCoverForm

    def form_valid(self, form):
        cover = form.cleaned_data['cover']
        self.object = form.save(commit=False)
        if (self.object.owner == getattr(cover, 'owner', None)
                == self.request.user):
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
