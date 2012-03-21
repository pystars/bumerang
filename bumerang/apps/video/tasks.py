# -*- coding: utf-8 -*-
import os
import random
import subprocess
import tempfile

from PIL import Image
from django.conf import settings
from celery.task import Task
from django.core.files.uploadedfile import InMemoryUploadedFile

from bumerang.apps.utils.functions import thumb_img
from models import Preview, Video
from converting.models import ConvertOptions


class MakeScreenShots(Task):
    queue = 'celery'

    def run(self, video_id, **kwargs):
        """
        Converts the Video and creates the related files.
        """
        logger = self.get_logger(**kwargs)
        Video.objects.filter(pk=video_id).update(status=Video.CONVERTING)
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return 'Video was deleted'
        logger.info("Starting Video Post conversion: %s" % video)
        #TODO: get file from s3 one time, make screen shots
        for preview in video.preview_set.all():
            preview.delete()
        options = ConvertOptions.objects.get(title='hq_file')
        size = '{0}x{1}'.format(options.width, options.height)
        source_file = tempfile.NamedTemporaryFile()
        source_file.write(video.best_quality_file().read())
        source_file.seek(0)
        video.best_quality_file().open()
        duration = video.seconds_duration()
        if duration > 30:
            offset = 10
        else:
            offset = 1
        screenable_duration = duration - offset * 2
        previews_count = settings.PREVIEWS_COUNT
        if screenable_duration < 1:
            previews_count = screenable_duration = 1
        elif screenable_duration < previews_count:
            previews_count = screenable_duration
        step = screenable_duration / previews_count
        counter = 0
        while counter < previews_count:
            result_file = tempfile.NamedTemporaryFile()
            preview = Preview(owner=video)
            cmd = self.get_commandline(source_file.name, random.choice(
                range(offset, offset+step)), size, result_file.name)
            process = subprocess.call(cmd, shell=False)
            if process:
                return "Stop Making screenshots - video is deleted"
            img = Image.open(result_file.name).copy()
            result_file.close()
            preview.image = thumb_img(img)
            preview.thumbnail = thumb_img(img)
            preview.icon = thumb_img(img)
            preview.save()
            offset += step
            counter += 1
        Video.objects.filter(pk=video_id).update(status=Video.READY)
        return "Ready"

    def get_commandline(self, path, offset, size, output):
        return ['ffmpeg', '-y', '-itsoffset', '-{0}'.format(offset), '-i', path,
            '-vframes', '1', '-an', '-vcodec', 'mjpeg', '-f', 'rawvideo',
            '-s', size, output]


class ConvertVideoTask(Task):
    queue = 'video'

    def get_commandline(self):
        return (['HandBrakeCLI', '-v3', '-O', '-C', '2', '-i',
            self.temporarily_original_copy.name]
            + self.convert_options + ['-o', self.temporarily_result_file.name])

    def run(self, video_id, **kwargs):
        """
        Converts the Video and creates the related files.
        """
        #TODO: what if user update videofile during converting
        logger = self.get_logger(**kwargs)
        print 'logfile:', self.request.logfile
        print 'kwargs:', kwargs
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return "Stop Convert - video is deleted"
        logger.info("Starting Video Post conversion: %s" % video)
        self.temporarily_original_copy = tempfile.NamedTemporaryFile()
        self.temporarily_original_copy.write(video.original_file.read())
        video.status = Video.CONVERTING
        Video.objects.filter(pk=video_id).update(status=Video.CONVERTING)
        for options in ConvertOptions.objects.all():
            file_field_name = options.title
            self.temporarily_result_file = tempfile.NamedTemporaryFile()
            self.convert_options = options.as_commandline()
            setattr(video, file_field_name, None)
            video.save()
            process = subprocess.call(self.get_commandline(), shell=False)
            try:
                video = Video.objects.get(pk=video_id)
            except Video.DoesNotExist:
                self.temporarily_original_copy.close()
                self.temporarily_result_file.close()
                return "Stop Convert - video is deleted"
            if process:
                stdout, stderr = process.communicate()
                print 'stdout:', stdout
                print 'stderr:', stderr
                video.status = video.ERROR
            else:
                size = os.path.getsize(self.temporarily_result_file.name)
                self.temporarily_result_file.seek(0)
                converted_file = InMemoryUploadedFile(
                    self.temporarily_result_file, None,
                    '{0}.mp4'.format(options.title), 'video/mp4', size, None)
                setattr(video, file_field_name, converted_file)
            video.save()
            self.temporarily_result_file.close()
        self.temporarily_original_copy.close()
        MakeScreenShots.delay(video_id)
        return "Ready"

