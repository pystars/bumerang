# -*- coding: utf-8 -*-
import os
import subprocess

from django.conf import settings
from celery.task import Task

from mediainfo import video_duration
from models import Preview
from converting.models import ConvertOptions


class ConvertVideoTask(Task):

    def get_commandline(self):
        return (['HandBrakeCLI', '-O', '-C', '2', '-i', self.original_file_path]
            + self.convert_options + ['-o', self.result_file])

    def get_screen_shots(self, video):
        for preview in video.preview_set.all():
            os.unlink(preview.image.path)
            preview.delete()
        options = ConvertOptions.objects.get(title='hq_file')
        size = '{0}x{1}'.format(options.width, options.height)
        offset = step = video.seconds_duration() / settings.PREVIEWS_COUNT
        offset -= 1
        source_path = video.best_quality_file().path
        while offset < video.seconds_duration():
            preview = Preview(owner=video)
            upload_to = preview.image.field.upload_to(
                preview, '{0}.jpg'.format(offset))
            output = preview.image.field.storage.path(upload_to)
            parent_path = os.path.split(output)[0]
            if not os.path.exists(parent_path):
                os.makedirs(parent_path)
            cmd = self.screen_shot_cmd(source_path, offset, size, output)
            print ' '.join(cmd)
            process = subprocess.call(cmd, shell=False)
            if not process:
                preview.image = upload_to
                preview.save()
            offset += step

    def screen_shot_cmd(self, path, offset, size, output):
        return ['ffmpeg', '-itsoffset', '-{0}'.format(str(offset)), '-i', path,
                '-vframes', '1', '-an', '-vcodec', 'mjpeg', '-f', 'rawvideo',
                '-s', size, output]

    def run(self, video, **kwargs):
        """
        Converts the Video and creates the related files.
        """
        logger = self.get_logger(**kwargs)
        logger.info("Starting Video Post conversion: %s" % video)

        self.original_file_path = video.original_file.path
        video.duration = video_duration(video.original_file.file)
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
            if process:
                video.status = video.ERROR
            else:
                video.status = video.READY
                setattr(video, file_field_name, upload_to)
                video.save()
        self.get_screen_shots(video)
        return "Ready"
