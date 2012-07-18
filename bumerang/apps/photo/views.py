# -*- coding: utf-8 -*-
import json

from PIL import Image
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models.expressions import F
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import ModelFormMixin, UpdateView, BaseFormView
from django.views.generic.list import MultipleObjectMixin
from bumerang.apps.photo.models import PhotoCategory

from bumerang.apps.utils.functions import thumb_img
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
            msg = u'Фото успешно перемещено'
        else:
            msg = u'Ошибка перемещения фото'
        return super(PhotoMoveView, self).render_to_response(message=msg)


class PhotoDetailView(DetailView):
    model = Photo

    def get(self, request, **kwargs):
        response = super(PhotoDetailView, self).get(request, **kwargs)
        self.get_queryset().filter(pk=self.object.id).update(
            views_count=F('views_count') + 1)
        return response


def increase_views_count(request, pk):
    if request.method == 'GET':
        photo = Photo.objects.filter(pk=pk)
        photo.update(views_count=F('views_count') + 1)

        photo_object = photo[0]

        return HttpResponse(json.dumps(
                {'error': False,
                 'views_count': photo_object.views_count}
        ), status=200)


class PhotoEditMixin(object):
    def make_thumbs(self):
        img = Image.open(self.object.original_file.file).copy()
        img = img.convert('RGB')
        self.object.original_file.file.seek(0)
        self.object.image = thumb_img(img, 938)
        self.object.thumbnail = thumb_img(img, 190)
        self.object.icon = thumb_img(img, 60)
        del img
        self.object.save()


class PhotoCreateView(CreateView, PhotoEditMixin):
    model = Photo

    def get_form(self, form_class):
        if self.album():
            return AlbumPhotoCreateForm(
                self.request.user, **self.get_form_kwargs())
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
        self.make_thumbs()
        return super(ModelFormMixin, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.ERROR, u'Ошибка при загрузке фото')
        return super(PhotoCreateView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super(PhotoCreateView, self).get_context_data(**kwargs)
        ctx.update({'photo_album': self.album()})
        return ctx

    def get_success_url(self):
        if 'photo_album_id' in self.kwargs:
            return reverse('photo-album-detail',
            args=[self.kwargs['photo_album_id']])
        else:
            return reverse('profile-photo-detail', args=[self.request.user.profile.id])

class PhotoUpdateView(OwnerMixin, UpdateView, PhotoEditMixin):
    model = Photo

    def get_form(self, form_class):
        return PhotoForm(self.request.user, **self.get_form_kwargs())

    def get_success_url(self):
        return reverse('photo-edit', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        if 'original_file' in form.changed_data:
            self.object = form.save(commit=False)
            self.make_thumbs()
        else:
            self.object = form.save()
        messages.add_message(self.request, messages.SUCCESS,
            u'Информация о фото успешно обновлена')
        return super(ModelFormMixin, self).form_valid(form)


class PhotoAlbumMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super(PhotoAlbumMixin, self).get_context_data(**kwargs)
        ctx['photo_categories'] = PhotoCategory.objects.all()
        try:
            ctx['current_category'] = self.current_category
        except AttributeError:
            pass

        return ctx


class PhotoListView(ListView):
    paginate_by = 25

    def get_queryset(self):
        qs = super(PhotoListView, self).get_queryset()
        try:
            self.current_category = PhotoCategory.objects.get(
                slug=self.kwargs['category'])
            qs = qs.filter(category=self.current_category)
        except PhotoCategory.DoesNotExist:
            return qs.none()
        except KeyError:
            pass

        qs = qs.filter(
            published_in_archive=True,
        )
        return qs


class PhotoAlbumListView(PhotoAlbumMixin, ListView):
    queryset = PhotoAlbum.objects.filter(
        cover__isnull = False,
    )
    paginate_by = 5