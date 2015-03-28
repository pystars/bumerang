# -*- coding: utf-8 -*-
import json
import re

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from boto import elastictranscoder

from bumerang.apps.video.utils import hq_upload_to
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


def convert_original_video(sender, **kwargs):
    """
    Receive message from AWS SNS about S3 file upload and check if it's an
     original video.
    """
    message = kwargs['message']
    # bucket_name = message['bucket']['name']
    for record in message['Records']:
        key = record['s3']['object']['key']
        pattern = re.compile('videos/(?P<slug>\w{12})/original.*')
        match = re.match(pattern, key)
        if match:
            slug = match.group('slug')
            from bumerang.apps.video.models import Video
            video = Video.objects.get(slug=slug)
            encoder = Transcoder(settings.AWS_ELASTICTRANCODER_PIPELINE)
            encoder.encode(
                {'Key': key},
                {'Key': hq_upload_to(video, None),
                 'PresetId': settings.AWS_ELASTICTRANCODER_PRESET}
            )
            print(type(encoder.message))
            print(encoder.message)
            info = json.loads(encoder.message)
            EncodeJob.objects.create(
                content_type=ContentType.objects.get_for_model(Video),
                object_pk=video.pk,
                job_id=info['jobId']
            )


def update_encode_state(sender, **kwargs):
    message = kwargs['message']
    job_id = message['jobId']
    state = message['state']
    job = EncodeJob.objects.get(pk=job_id)
    from bumerang.apps.video.models import Video

    if state == 'PROGRESSING':
        job.message = 'Progressing'
        job.state = EncodeJob.PROGRESSING
        job.content_object.status = Video.CONVERTING
    elif state == 'WARNING':
        job.message = 'Warning'
        job.state = EncodeJob.WARNING
    if state == 'COMPLETED':
        job.message = 'Success'
        job.state = EncodeJob.COMPLETED
        job.content_object.status = Video.READY
        job.content_object.original_file = ''
        job.content_object.hq_file = ''
    if state == 'ERROR':
        job.message = message['messageDetails']
        job.state = EncodeJob.ERROR
        job.content_object.status = Video.ERROR
    job.content_object.save()
    job.save()
