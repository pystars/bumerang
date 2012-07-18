# -*- coding: utf-8 -*-
from __future__ import division
import time

from django import template
from django.utils.timezone import now

register = template.Library()

@register.filter
def to_hms(value):
    #not more than 24 hours, please
    total_time = time.gmtime(int((value or 0)/1000))
    time_format = '%H:%M:%S' if total_time.tm_hour else '%M:%S'
    return time.strftime(time_format, total_time)

@register.filter
def is_future(value):
    return value.play_from() > now()

@register.filter
def is_now(value):
    return value.play_from() < now() < value.play_till()
