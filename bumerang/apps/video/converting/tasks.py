# -*- coding: utf-8 -*-
import os
import random
import subprocess
from tempfile import NamedTemporaryFile  # , mktemp

from PIL import Image
from celery.task import Task
from django.conf import settings

# from django.core.files.uploadedfile import InMemoryUploadedFile

from ...utils.functions import thumb_img
from .mediainfo import media_info
from .models import ConvertOptions


class MakeScreenShots(Task):
    queue = 'celery'

    def run(self, video_id, **kwargs):
        """
        Converts the Video and creates the related files.
        """
        logger = self.get_logger(**kwargs)
        from ..models import Preview, Video

        Video.objects.filter(pk=video_id).update(status=Video.CONVERTING)
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return 'Video was deleted'
        logger.info("Starting screen shoots of video %s" % video.pk)
        for preview in video.preview_set.all():
            preview.delete()
        options = ConvertOptions.objects.get(title='hq_file')
        source_file = NamedTemporaryFile(
            delete=False, suffix='.mp4', prefix='screen_shot_source')
        source_file.write(video.best_quality_file().read())
        logger.info("Downloaded best {0} ({1})".format(video, source_file.name))
        source_file.close()
        try:
            file_params = media_info(source_file.name)
        except OSError:
            self._error_handle(video)
            return "Stop screenshoot - bad source file"
        if not file_params.get('Video', None):
            self._error_handle(video)
            return "Stop screenshoot - bad source file"
        options.update(file_params)
        size = '{0}x{1}'.format(options.width, options.height)
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
        for offset in (offset+step for i in xrange(previews_count)):
            result_file = NamedTemporaryFile(
                suffix='.jpg', prefix='screen_shot')
            preview = Preview(owner=video)
            cmd = self.get_commandline(source_file.name, random.choice(
                range(offset, offset+step)), size, result_file.name)
            process = subprocess.call(cmd, shell=False)
            if process:
                Video.objects.filter(pk=video_id).update(status=Video.ERROR)
                logger.error("Some error during ffmpeging %s" % video.pk)
                return "Stop making screen shoots - video is deleted"
            try:
                orig = Image.open(result_file.name)
                img = orig.copy()
                result_file.close()
                preview_name = '{0}.jpg'.format(offset)
                preview.image = thumb_img(img, name=preview_name)
                preview.thumbnail = thumb_img(img, 190, name=preview_name)
                preview.icon = thumb_img(img, 60, name=preview_name)
                preview.save()
            except IOError:
                result_file.close()
                logger.error('error during imagining {0}'.format(
                    result_file.name))
        logger.info("Screened {0} ({1})".format(video, source_file.name))
        os.unlink(source_file.name)
        Video.objects.filter(pk=video_id).update(status=Video.READY)
        return "Ready"

    def get_commandline(self, path, offset, size, output):
        return ['ffmpeg', '-y', '-itsoffset', '-{0}'.format(offset), '-i', path,
            '-vframes', '1', '-an', '-vcodec', 'mjpeg', '-f', 'rawvideo',
            '-s', size, output]


# class ConvertVideoTask(Task):
#     queue = 'video'
#
#     def get_commandline(self):
#         return (['HandBrakeCLI', '-v3', '-O', '-C', '2', '-i',
#             self.original_copy.name]
#             + self.convert_options + ['-o', self.result_file_name])
#
#     def _error_handle(self, video):
#         video.status = Video.ERROR
#         video.save()
#         os.unlink(self.original_copy.name)
#
#     def run(self, video_id, **kwargs):
#         """
#         Converts the Video and creates the related files.
#         """
#         #TODO: what if user update videofile during converting
#         logger = self.get_logger(**kwargs)
#         try:
#             video = Video.objects.get(pk=video_id)
#         except Video.DoesNotExist:
#             return "Stop Convert - video is deleted"
#         logger.info("Starting Video Post conversion: %s" % video)
#         ext = os.path.splitext(video.original_file.name)[1]
#         self.original_copy = NamedTemporaryFile(delete=False,
#             prefix='video_source', suffix=ext)
#         self.original_copy.write(video.original_file.file.read())
#         video.original_file.open()
#         self.original_copy.close()
#         try:
#             file_params = media_info(self.original_copy.name)
#         except OSError:
#             self._error_handle(video)
#             return "Stop Convert - bad original file"
#         if not file_params.get('Video', None):
#             self._error_handle(video)
#             return "Stop Convert - bad original file"
#         video.duration = file_params['Video']['Duration']
#         video.status = Video.CONVERTING
#         video.save()
#         for options in ConvertOptions.objects.all():
#             options.update(file_params)
#             file_field_name = options.title
#             self.result_file_name = mktemp('.mp4', 'video')
#             self.convert_options = options.as_commandline()
#             setattr(video, file_field_name, None)
#             video.save()
#             process = subprocess.call(self.get_commandline(), shell=False)
#             logger.info("Processed {0} ({1})".format(video, options.title))
#             try:
#                 video = Video.objects.get(pk=video_id)
#             except Video.DoesNotExist:
#                 os.unlink(self.original_copy.name)
#                 os.unlink(self.result_file_name)
#                 return "Stop Convert - video is deleted"
#             if process:
#                 logger.error("some error during convert: %s" % video)
#                 stdout, stderr = process.communicate()
#                 logger.error('stdout: {0}'.format(stdout))
#                 logger.error('stderr: {0}'.format(stderr))
#                 video.status = Video.ERROR
#             else:
#                 size = os.path.getsize(self.result_file_name)
#                 converted_file = InMemoryUploadedFile(
#                     open(self.result_file_name), None,
#                     '{0}.mp4'.format(options.title), 'video/mp4', size, None)
#                 setattr(video, file_field_name, converted_file)
#             video.save()
#             os.unlink(self.result_file_name)
#             logger.info("Saved {0} of {1} (was {2})".format(options.title,
#                 video, self.result_file_name))
#         os.unlink(self.original_copy.name)
#         logger.info('Convert of {0} ready'.format(video))
#         if video.best_quality_file():
#             logger.info('Send task to screen {0}'.format(video))
#             MakeScreenShots.delay(video_id)
#         return "Ready"
