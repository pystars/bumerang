# -*- coding: utf-8 -*-
from __future__ import division

from django import template

register = template.Library()


@register.filter
def minutes_to_hms(value):
    return seconds_to_hms(value * 60)


@register.filter
def seconds_to_hms(value):
    hours = value // 3600
    minutes = value % 3600 // 60
    seconds = value % 60
    return u'{0:02d}:{1:02d}:{2:02d}'.format(hours, minutes, seconds)


@register.filter
def milliseconds_to_hms(value):
    return seconds_to_hms(value // 1000)


@register.filter
def seconds_to_hm(value):
    hours = value // 3600
    minutes = value % 3600 // 60
    return u'{0:02d}:{1:02d}'.format(hours, minutes)
