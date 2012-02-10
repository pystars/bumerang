# -*- coding: utf-8 -*-
import subprocess

from celery.task import Task

from apps.video.mediainfo import video_duration
from converting.models import ConvertOptions


class ConvertVideoTask(Task):

    def get_commandline(self):
        return (
            ['HandBrakeCLI', '-O', '-C', '2', '-i', self.original_file_path]
            + self.convert_options + ['-o', self.result_file]
        )

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
            field = getattr(video, options.title).field
            self.result_file = field.storage.path(field.upload_to(video, ''))
            self.convert_options = options.as_commandline()
            setattr(video, options.title, None)
            video.save()
            process = subprocess.call(self.get_commandline(), shell=False)
            if process:
                video.status = video.ERROR
            else:
                video.status = video.READY
                setattr(video, options.title, self.result_file)
                video.save()
        return "Ready"
