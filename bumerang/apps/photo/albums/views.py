# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin
from django.views.generic.detail import DetailView

from bumerang.apps.utils.views import OwnerMixin, AjaxView
from forms import PhotoAlbumForm, PhotoAlbumCoverForm
from models import PhotoAlbum


class PhotoSetCoverView(AjaxView, UpdateView):
    model = PhotoAlbum
    form_class = PhotoAlbumCoverForm

    def form_valid(self, form):
        msg = u'Обложка альбома изменена'
        return super(PhotoSetCoverView, self).render_to_response(message=msg)

    def get_success_url(self):
        messages.add_message(
            self.request, messages.SUCCESS, u'Обложка фотоальбома обновлена')
        return reverse('photo-album-detail', args=[self.object.id])


class PhotoAlbumUpdateView(OwnerMixin, UpdateView):
    model = PhotoAlbum
    form_class = PhotoAlbumForm

    def get_success_url(self):
        return reverse('photo-album-detail', kwargs={'pk': self.object.id})


class PhotoAlbumCreateView(CreateView):
    model = PhotoAlbum
    form_class = PhotoAlbumForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return super(ModelFormMixin, self).form_valid(form)

    def get_success_url(self):
        return reverse('album-photo-add',
            kwargs={'photo_album_id': self.object.id})


class PhotoAlbumDetailView(DetailView):
    model = PhotoAlbum

    def get_context_data(self, **kwargs):
        photos = self.object.photo_set.all()
        ctx = super(PhotoAlbumDetailView, self).get_context_data(**kwargs)
        ctx['photos'] = photos
        return ctx