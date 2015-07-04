# -*- coding: utf-8 -*-
import os
from string import lower

from django.conf import settings
from django.core.exceptions import ValidationError


def is_video_file(field):
    ext = lower(os.path.splitext(field.name)[1][1:])
    if ext not in settings.SUPPORTED_VIDEO_FORMATS:
        raise ValidationError(u'неправильный видеофайл')


def digital_name(value):
    try:
        int(value.name.split('.')[0])
    except ValueError:
        raise ValidationError(u'Имя скриншота должно представлять собой '
                              u'секунду, на которой он сделан, например 6.jpg')
    return value
