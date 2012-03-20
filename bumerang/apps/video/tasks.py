# -*- coding: utf-8 -*-
import os
import random
import shutil
import subprocess
import tempfile

from PIL import Image
from django.conf import settings
from celery.task import Task

from bumerang.apps.utils.functions import thumb_img
from models import Preview, Video
from converting.models import ConvertOptions


class MakeScreenShots(Task):
    def run(self, video, **kwargs):
        """
        Converts the Video and creates the related files.
        """
        logger = self.get_logger(**kwargs)
        logger.info("Starting Video Post conversion: %s" % video)
        #TODO: get file from s3 one time, make screen shots
        Video.objects.filter(pk=video.id).update(status=video.CONVERTING)
        for preview in video.preview_set.all():
#            os.remove(preview.image.path)
            preview.delete()
        options = ConvertOptions.objects.get(title='hq_file')
        size = '{0}x{1}'.format(options.width, options.height)
        source_path = video.best_quality_file().path
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
            tmp_file = tempfile.NamedTemporaryFile()
            preview = Preview(owner=video)
            cmd = self.get_commandline(source_path,
                random.choice(range(offset, offset+step)), size, tmp_file.name)
            process = subprocess.call(cmd, shell=False)
            if process:
                return "Stop Making screenshots - video is deleted"
            img = Image.open(tmp_file.name).copy()
            tmp_file.close()
            preview.image = thumb_img(img)
            preview.thumbnail = thumb_img(img)
            preview.icon = thumb_img(img)
            preview.save()
            offset += step
            counter += 1
        try:
            video = Video.objects.get(pk=video.id)
        except Video.DoesNotExist:
            return "Stop Making screenshots - video is deleted"
        video.status = Video.READY
        video.save()
        return "Ready"

    def get_commandline(self, path, offset, size, output):
        return ['ffmpeg', '-y', '-itsoffset', '-{0}'.format(offset), '-i', path,
            '-vframes', '1', '-an', '-vcodec', 'mjpeg', '-f', 'rawvideo',
            '-s', size, output]


class ConvertVideoTask(Task):

    def get_commandline(self):
        return (['HandBrakeCLI', '-v3', '-O', '-C', '2', '-i',
            self.original_file_path]
            + self.convert_options + ['-o', self.result_file])

    def run(self, video, **kwargs):
        """
        Converts the Video and creates the related files.
        """
        #TODO: what if user update videofile during converting
        #TODO: rewrite it to work with s3
        logger = self.get_logger(**kwargs)
        print 'logfile:', self.request.logfile
        print 'kwargs:', kwargs
        logger.info("Starting Video Post conversion: %s" % video)

        self.original_file_path = video.original_file.path
        video.status = video.CONVERTING
        video.save()
        for options in ConvertOptions.objects.all():
            file_field_name = options.title
            field = getattr(video, file_field_name).field
            upload_to = field.upload_to(video, '')
            self.result_file = field.storage.path(upload_to)
            self.convert_options = options.as_commandline()
            setattr(video, file_field_name, None)
            video.save()
            process = subprocess.call(self.get_commandline(), shell=False)
            try:
                video = Video.objects.get(pk=video.id)
            except Video.DoesNotExist:
                shutil.rmtree(os.path.split(upload_to)[0], ignore_errors=True)
                return "Stop Convert - video is deleted"
            if process:
                stdout, stderr = process.communicate()
                print 'stdout:', stdout
                print 'stderr:', stderr
                video.status = video.ERROR
            else:
                setattr(video, file_field_name, upload_to)
            video.save()

        MakeScreenShots.delay(video)
        return "Ready"

