# -*- coding: utf-8 -*-
from __future__ import division
import time

from django import template

register = template.Library()

@register.filter
def to_hm(value, is_last=False):
    #time_val = time.gmtime(int(value.offset/1000))
    rotate = value.playlist.rotate_from
    offset_time = rotate.second + rotate.minute*60 + rotate.hour*60**2 + int(value.offset/1000)
    total_time = time.gmtime(offset_time)
    if is_last:
        total_time = time.gmtime(offset_time+int(value.video.duration/1000))
    return time.strftime('%H:%M', total_time)

#@register.filter
#def last_to_hm(value):
#    total = int((value.offset + value.video.duration)/1000)
#    time_val = time.gmtime(total)
#    return time.strftime('%H:%M', time_val)

@register.filter
def is_future(value):
    now = time.localtime()
    now_secs = now.tm_sec + now.tm_min*60 + now.tm_hour*60**2
    rotate = value.playlist.rotate_from
    offset_time = rotate.second + rotate.minute*60 + rotate.hour*60**2 + int(value.offset/1000)

    if offset_time > now_secs:
        return True
    else:
        return False