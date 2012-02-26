# -*- coding: utf-8 -*-
import json

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import ModelFormMixin, UpdateView, BaseFormView
from django.views.generic.list import MultipleObjectMixin

from bumerang.apps.utils.views import AjaxView, OwnerMixin
from albums.models import PhotoAlbum
from models import Photo
from forms import (PhotoForm, PhotoUpdateAlbumForm, PhotoCreateForm,
    AlbumPhotoCreateForm)


class PhotoMoveView(AjaxView, OwnerMixin, BaseFormView, MultipleObjectMixin):
    model = Photo
    form_class = PhotoUpdateAlbumForm
    
    def get_queryset(self, **kwargs):
        return super(PhotoMoveView, self).get_queryset(**kwargs)

    def form_valid(self, form):
        try:
            kwargs = dict(pk=int(form.cleaned_data['photo_id']))
        except ValueError:
            try:
                kwargs = dict(id__in=map(int,
                    json.loads(form.cleaned_data['photo_id'])))
            except ValueError:
                return HttpResponseForbidden()
        album = get_object_or_404(PhotoAlbum, pk=form.cleaned_data['album_id'],
            owner=self.request.user)
        if self.get_queryset().filter(**kwargs).update(album=album):
            msg = u'Видео успешно перемещено'
        else:
            msg = u'Ошибка перемещения видео'
        return super(PhotoMoveView, self).render_to_response(message=msg)


class PhotoDetailView(DetailView):
    model = Photo

    def get(self, request, **kwargs):
        response = super(PhotoDetailView, self).get(request, **kwargs)
        self.get_queryset().filter(pk=self.object.id).update(
            views_count=self.object.views_count + 1)
        return response


class PhotoCreateView(CreateView):
    model = Photo

    def get_form(self, form_class):
        if self.album():
            return AlbumPhotoCreateForm(**self.get_form_kwargs())
        return PhotoCreateForm(self.request.user, **self.get_form_kwargs())

    def album(self):
        if 'photo_album_id' in self.kwargs:
            try:
                return PhotoAlbum.objects.get(
                    owner=self.request.user, pk=self.kwargs['photo_album_id'])
            except PhotoAlbum.DoesNotExist:
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
        return super(PhotoCreateView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super(PhotoCreateView, self).get_context_data(**kwargs)
        ctx.update({'photo_album': self.album()})
        return ctx


class PhotoUpdateView(OwnerMixin, UpdateView):
    model = Photo

    def get_form(self, form_class):
        return PhotoForm(self.request.user, **self.get_form_kwargs())

    def get_success_url(self):
        return reverse('photo-edit', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        if 'original_file' in form.changed_data:
            self.object.duration = photo_duration(
                form.cleaned_data['original_file'].temporary_file_path())
        self.object = form.save()
        messages.add_message(self.request, messages.SUCCESS,
            u'Информация о видео успешно обновлена')
        return super(PhotoUpdateView, self).form_valid(form)


class PhotoListView(ListView):
    queryset = Photo.objects.filter(
        published_in_archive=True,
    )
    paginate_by = 25
