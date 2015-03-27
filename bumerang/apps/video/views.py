# -*- coding: utf-8 -*-
from datetime import datetime
import json
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Avg
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import F, Q
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView
from django.views.generic.detail import DetailView, BaseDetailView, \
    SingleObjectMixin
from django.views.generic.edit import ModelFormMixin, UpdateView, BaseFormView, \
    FormMixin, ProcessFormView
from django.views.generic.list import MultipleObjectMixin
from django.contrib.auth import get_user_model
from djcelery.views import JsonResponse
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import mail_admins
from bumerang.apps.utils.transcoder import Transcoder
from bumerang.apps.video.utils import hq_upload_to

from .signals import (
    transcode_onprogress,
    transcode_onerror,
    transcode_oncomplete,
    transcode_onwarning)

from bumerang.apps.video.utils import original_upload_to
from bumerang.apps.utils.s3 import create_upload_data
from bumerang.apps.utils.views import AjaxView, OwnerMixin
from albums.models import VideoAlbum
from .models import Video, VideoCategory#, EncodeJob
from bumerang.apps.events.models import ParticipantVideo, ParticipantVideoScore
from forms import VideoForm, VideoUpdateAlbumForm, VideoCreateForm, \
    GetS3UploadURLForm


Profile = get_user_model()


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
    fields = (
        'title',
        'album',
        'category',
        'description'
    )

    def get_form(self, form_class):
        return VideoCreateForm(self.request.user, **self.get_form_kwargs())

    def get_initial(self):
        result = super(VideoCreateView, self).get_initial()
        result.update(album=self.kwargs.get('video_album_id', None))
        return result

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return super(ModelFormMixin, self).form_valid(form)

    def get_success_url(self):
        return reverse('video-edit', kwargs={'pk': self.object.id})


class VideoUpdateView(OwnerMixin, UpdateView):
    model = Video

    def get_form(self, form_class):
        return VideoForm(self.request.user, **self.get_form_kwargs())

    def get_success_url(self):
        return reverse('video-edit', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        self.object = form.save()
        messages.add_message(
            self.request, messages.SUCCESS,
            u'Информация о видео успешно обновлена')
        return HttpResponseRedirect(self.get_success_url())


class VideoGetS3UploadURLView(OwnerMixin, FormMixin, SingleObjectMixin,
                              ProcessFormView):
    """
    Returns data for upload to S3 and creates EncodeJob for call it back
    later and start converting job.
    We need it to prevent reusing of link which should be used once.
    """
    form_class = GetS3UploadURLForm
    model = Video
    allowed_methods = ['post']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(
            VideoGetS3UploadURLView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        content_type = form.cleaned_data['content_type']
        if not content_type.startswith('video/'):
            data = json.dumps(
                {'error': 'Invalid file type (%s).' % content_type})
            return HttpResponseBadRequest(
                data, content_type="application/json", status=400)
        key = original_upload_to(self.object, form.cleaned_data['filename'])
        self.object.original_file = key
        self.object.save()
        data = create_upload_data(
            content_type,
            key,
            'public-read',
            settings.AWS_MEDIA_STORAGE_BUCKET_NAME
        )
        # EncodeJob.objects.create(
        #     signature=data['signature'],
        #     content_type=ContentType.objects.get_for_model(Video),
        #     object_pk=self.object.pk
        # )
        return HttpResponse(json.dumps(data), content_type="application/json")

    def form_invalid(self, form):
        return HttpResponseBadRequest(
            json.dumps(form.errors), content_type="application/json")


class ConvertJobCallbackView(OwnerMixin, BaseDetailView):
    """
    Callback view which should be touched when S3 upload is finished.
    It starts encoding job in AWS elastictranscoder.
    """
    # model = EncodeJob
    slug_field = 'signature'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.content_object.owner is not self.request.user:
            return HttpResponseForbidden('sorry, no permission')
        if self.object.is_activated:
            return HttpResponseForbidden('sorry, already used')
      # # encoder = Transcoder(settings.AWS_ELASTICTRANCODER_PIPELINE)
        # encoder.encode(
        #     {'Key': str(self.object.content_object.original_file)},
        #     {'Key': hq_upload_to(self.object.content_object, None),
        #      'PresetId': settings.AWS_ELASTICTRANCODER_PRESET}
        # )
        # self.object.is_activated = True
        # self.object.job_id = encoder.message['jobId']
        # self.object.save()
        # TODO: should we save JobId here?
        return HttpResponse(
            json.dumps({'status': 'ok'}), content_type="application/json")


@csrf_exempt
def endpoint(request):
    """
    Receive SNS notification and update related EncodeJob status
    """

    try:
        data = json.loads(request.read())
    except ValueError:
        return HttpResponseBadRequest('Invalid JSON')

    print(data)
    # handle SNS subscription
    if data['Type'] == 'SubscriptionConfirmation':
        subscribe_url = data['SubscribeURL']
        subscribe_body = """
        Please visit this URL below to confirm your subscription with SNS
        %s """ % subscribe_url

        mail_admins('Please confirm SNS subscription', subscribe_body)
        return HttpResponse('OK')

    try:
        message = json.loads(data['Message'])
    except ValueError:
        assert False, data['Message']

    # if message['state'] == 'PROGRESSING':
    #     job = EncodeJob.objects.get(job_id=message['jobId'])
    #     job.message = 'Progressing'
    #     job.state = EncodeJob.PROGRESSING
    #     job.save()
    #     transcode_onprogress.send(sender=None, job=job, message=message)
    #
    # elif message['state'] == 'WARNING':
    #     job = EncodeJob.objects.get(job_id=message['jobId'])
    #     job.message = 'Warning'
    #     job.state = EncodeJob.WARNING
    #     job.save()
    #     transcode_onwarning.send(sender=None, job=job, message=message)
    #
    # elif message['state'] == 'COMPLETED':
    #     job = EncodeJob.objects.get(job_id=message['jobId'])
    #     job.message = 'Success'
    #     job.state = EncodeJob.COMPLETE
    #     job.save()
    #     transcode_oncomplete.send(sender=None, job=job, message=message)
    #
    # elif message['state'] == 'ERROR':
    #     job = EncodeJob.objects.get(job_id=message['jobId'])
    #     job.message = message['messageDetails']
    #     job.state = EncodeJob.ERROR
    #     job.save()
    #     transcode_onerror.send(sender=None, job=job, message=message)

    return HttpResponse('Done')


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
        if self.request.GET.get('q', None):
            phrase = self.request.GET['q']
            qs = qs.filter(Q(title__icontains=phrase) |
                           Q(owner__title__icontains=phrase) |
                           Q(owner__username__icontains=phrase) |
                           Q(city__icontains=phrase) |
                           Q(authors__icontains=phrase) |
                           Q(teachers__icontains=phrase) |
                           Q(manager__icontains=phrase) |
                           Q(festivals__icontains=phrase))
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

            filter = {'owner': self.object}
            if req_type == 'videos_with_no_album':
                filter['album'] = None

            videos_qs = Video.objects.filter(**filter)

            videos_list = videos_qs.values(*videos_fields)
            result['videos_list'] = list(videos_list)

        return self.render_to_response(json.dumps(result))
