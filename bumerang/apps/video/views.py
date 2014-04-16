# -*- coding: utf-8 -*-
from datetime import datetime

from django.db.models.aggregates import Avg
from django.utils import simplejson
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import F
from django.http import (HttpResponseForbidden, HttpResponseRedirect,
    HttpResponse)
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import ModelFormMixin, UpdateView, BaseFormView
from django.views.generic.list import MultipleObjectMixin

#from bumerang.apps.accounts.models import Profile
from bumerang.apps.accounts.models import CustomUser as Profile
from bumerang.apps.utils.views import AjaxView, OwnerMixin
from albums.models import VideoAlbum
from models import Video, VideoCategory
from bumerang.apps.events.models import ParticipantVideo, ParticipantVideoScore
from tasks import ConvertVideoTask
from forms import VideoForm, VideoUpdateAlbumForm, VideoCreateForm


class VideoMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super(VideoMixin, self).get_context_data(**kwargs)
        ctx['video_categories'] =VideoCategory.objects.all()
        try:
            ctx['current_category'] = self.current_category
        except AttributeError:
            pass
        return ctx


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
                    simplejson.loads(form.cleaned_data['video_id'])))
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


class VideoDetailView(VideoMixin, DetailView):
    model = Video

    def get_context_data(self, **kwargs):
        ctx = super(VideoDetailView, self).get_context_data(**kwargs)
        if self.request.GET.get('pv', None):
            try:
                ctx['participant_video'] = ParticipantVideo.objects.filter(
                    video_id=self.object.pk,
                    participant__event__end_date__gte=datetime.now()).get(
                    pk=int(self.request.GET['pv']))
                current_score = ParticipantVideoScore.objects.get(
                        owner=self.request.user,
                        participant_video=ctx['participant_video']
                    )
                ctx['participant_video'].current_score = current_score
            except ParticipantVideoScore.DoesNotExist:
                ctx['participant_video'].current_score = None
            except ParticipantVideo.DoesNotExist, ValueError:
                pass
        return ctx

    def get_queryset(self):
        return super(VideoDetailView, self).get_queryset().filter(
            status=self.model.READY).annotate(avg_score=Avg(
            'participantvideo__participantvideoscore__score'))

    def get(self, request, **kwargs):
        response = super(VideoDetailView, self).get(request, **kwargs)
        Video.objects.filter(pk=self.object.id).update(
            views_count=F('views_count') + 1)
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
        if not self.object.title:
            self.object.title = self.object.original_file.name
        self.object.save()
        ConvertVideoTask.delay(self.object.id)
        messages.add_message(
            self.request, messages.SUCCESS, u"""
            Видео успешно загружено и находится в обработке.
            Пожалуйста заполните поля с описанием вашей работы.""")
        return super(ModelFormMixin, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.ERROR, u"""
            Во время загрузки произошла непредвиденная ошибка.
            Техническая поддержка уже вкурсе""")
        return super(VideoCreateView, self).form_invalid(form)

    def get_success_url(self):
        return reverse('video-edit', kwargs={'pk': self.object.id})

class VideoUpdateView(OwnerMixin, UpdateView):
    model = Video

    def get_form(self, form_class):
        return VideoForm(self.request.user, **self.get_form_kwargs())

    def get_success_url(self):
        return reverse('video-edit', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if 'original_file' in form.changed_data:
            self.object.status = Video.PENDING
            self.object.save()
            ConvertVideoTask.delay(self.object.id)
        else:
            self.object.save()
        messages.add_message(self.request, messages.SUCCESS,
            u'Информация о видео успешно обновлена')
        return HttpResponseRedirect(self.get_success_url())


class VideoListView(VideoMixin, ListView):
    model = Video
    paginate_by = 25

    def get_queryset(self):
        qs = super(VideoListView, self).get_queryset()
        try:
            self.current_category = VideoCategory.objects.get(
                slug=self.kwargs['category'])
            qs = qs.filter(category=self.current_category)
        except VideoCategory.DoesNotExist:
            return qs.none()
        except KeyError:
            pass
        qs = qs.filter(
            hq_file__isnull=False,
            published_in_archive=True,
            status=Video.READY
        )
        qs = qs.annotate(avg_score=Avg(
            'participantvideo__participantvideoscore__score'))
        return qs


class VideoListAjaxView(DetailView):
    model = Profile
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(context, **response_kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        req_type = request.GET.get('type')

        result = {}

        if req_type == 'albums':

            albums_fields = ['id', 'title', 'description', 'cover']
            albums_qs = VideoAlbum.objects.filter(owner=self.object)
            albums_list = albums_qs.values(*albums_fields)
            result['albums_list'] = list(albums_list)

        if req_type == 'videos' or req_type == 'videos_with_no_album':

            videos_fields = ['id', 'title', 'description',
                             'album', 'original_file']

            filter = { 'owner': self.object }
            if req_type == 'videos_with_no_album':
                filter['album'] = None

            videos_qs = Video.objects.filter(**filter)

            videos_list = videos_qs.values(*videos_fields)
            result['videos_list'] = list(videos_list)



        serialized = simplejson.dumps(result)

        from time import sleep
        sleep(0.2)

        return self.render_to_response(serialized)
