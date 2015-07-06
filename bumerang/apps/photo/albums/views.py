# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from bumerang.apps.photo.albums.models import PhotoCategory

from bumerang.apps.utils.views import OwnerMixin, AjaxView
from forms import PhotoAlbumForm, PhotoAlbumCoverForm
from models import PhotoAlbum


class PhotoMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super(PhotoMixin, self).get_context_data(**kwargs)
        ctx['photo_categories'] = PhotoCategory.objects.all()
        try:
            ctx['current_category'] = self.current_category
        except AttributeError:
            pass

        return ctx


class PhotoSetCoverView(AjaxView, OwnerMixin, UpdateView):
    model = PhotoAlbum
    form_class = PhotoAlbumCoverForm

    def form_valid(self, form):
        album = form.save()
        album.save()
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
        kwargs['photos'] = self.object.photo_set.all()
        kwargs['profile'] = self.object.owner
        return super(PhotoAlbumDetailView, self).get_context_data(**kwargs)


class PhotoAlbumListView(PhotoMixin, ListView):
    model = PhotoAlbum
    paginate_by = 25

    def get_queryset(self):
        qs = super(PhotoAlbumListView, self).get_queryset()
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
        return qs.order_by('-created')
