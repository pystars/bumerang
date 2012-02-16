# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin

from bumerang.apps.utils.views import OwnerMixin
from forms import VideoAlbumForm, VideoAlbumCoverForm
from models import VideoAlbum


class VideoSetCoverView(UpdateView):
    model = VideoAlbum
    form_class = VideoAlbumCoverForm

    def get_success_url(self):
        messages.add_message(
            self.request, messages.SUCCESS, u'Обложка видеоальбома обновлена')
        return reverse('video-album-detail', args=[self.object.id])


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
