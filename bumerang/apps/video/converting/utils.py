# -*- coding: utf-8 -*-
import re

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from boto import elastictranscoder

from .tasks import MakeScreenShots
from bumerang.apps.video.utils import hq_upload_to
from bumerang.apps.utils.media_storage import media_storage
from .models import EncodeJob


class Transcoder(object):
    def __init__(self, pipeline_id, region=None, access_key_id=None,
                 secret_access_key=None):
        self.pipeline_id = pipeline_id

        if not region:
            region = getattr(settings, 'AWS_REGION', None)
        self.aws_region = region

        if not access_key_id:
            access_key_id = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        self.aws_access_key_id = access_key_id

        if not secret_access_key:
            secret_access_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        self.aws_secret_access_key = secret_access_key

        if self.aws_access_key_id is None:
            assert False, 'Please provide AWS_ACCESS_KEY_ID'

        if self.aws_secret_access_key is None:
            assert False, 'Please provide AWS_SECRET_ACCESS_KEY'

        if self.aws_region is None:
            assert False, 'Please provide AWS_REGION'

    def encode(self, input_name, outputs):
        encoder = elastictranscoder.connect_to_region(
            self.aws_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key)

        self.message = encoder.create_job(
            self.pipeline_id, input_name, outputs=outputs)


def encode_video(video, key=None):
    output = hq_upload_to(video, None)
    if video.hq_file:
        video.hq_file.delete(save=False)
        video.status = video.PENDING
        video.save()
    else:
        media_storage.delete(output)
    encoder = Transcoder(settings.AWS_ELASTICTRANCODER_PIPELINE)
    if key is None and video.original_file:
        key = video.original_file.name
    encoder.encode(
        {'Key': key},
        [{'Key': hq_upload_to(video, None),
         'PresetId': settings.AWS_ELASTICTRANCODER_PRESET}]
    )
    EncodeJob.objects.create(
        content_type=ContentType.objects.get_for_model(video.__class__),
        object_id=video.pk,
        job_id=encoder.message['Job']['Id']
    )


def convert_original_video(sender, **kwargs):
    """
    Receive message from AWS SNS about S3 file upload and check if it's an
     original video.
    """
    message = kwargs['message']
    for record in message['Records']:
        key = record['s3']['object']['key']

        # if original added
        pattern = re.compile('videos/(?P<slug>\w{12})/original.*')
        match = re.match(pattern, key)
        if match:
            slug = match.group('slug')
            from bumerang.apps.video.models import Video
            video = Video.objects.get(slug=slug)
            encode_video(video, key)


def update_encode_state(sender, **kwargs):
    message = kwargs['message']
    job_id = message['jobId']
    state = message['state']
    job = EncodeJob.objects.get(pk=job_id)
    obj = job.content_object
    from bumerang.apps.video.models import Video

    if state == 'PROGRESSING':
        job.message = 'Progressing'
        job.state = EncodeJob.PROGRESSING
        obj.status = Video.CONVERTING
    elif state == 'WARNING':
        job.message = 'Warning'
        job.state = EncodeJob.WARNING
    elif state == 'COMPLETED':
        job.message = 'Success'
        job.state = EncodeJob.COMPLETE
        obj.original_file = message['input']['key']
        obj.duration = message['outputs'][0]['duration'] * 1000
        obj.hq_file = message['outputs'][0]['key']
        obj.save()
        MakeScreenShots.delay(obj.pk)
    elif state == 'ERROR':
        job.message = message['messageDetails']
        job.state = EncodeJob.ERROR
        obj.status = Video.ERROR
    obj.save()
    job.save()
