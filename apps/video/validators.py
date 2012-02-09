# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError

from mediainfo import video_duration


def check_video_file(field):
    if 'temporary_file_path' in field.file:
        if not video_duration(field.file.temporary_file_path()):
            raise ValidationError('file fail')
